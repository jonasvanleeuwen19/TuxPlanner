from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/todos", tags=["todos"])


def _enrich_todos(todos: list, db: Session) -> List[schemas.TodoResponse]:
    """Attach session_count to each todo."""
    if not todos:
        return []
    todo_ids = [t.id for t in todos]
    rows = (
        db.query(models.TaskSession.todo_id)
        .filter(models.TaskSession.todo_id.in_(todo_ids))
        .all()
    )
    count_map: dict = {t.id: 0 for t in todos}
    for (tid,) in rows:
        if tid in count_map:
            count_map[tid] += 1
    results = []
    for todo in todos:
        data = schemas.TodoResponse.model_validate(todo)
        data.session_count = count_map.get(todo.id, 0)
        results.append(data)
    return results


def _enrich_todo(todo: models.Todo, db: Session) -> schemas.TodoResponse:
    session_count = (
        db.query(models.TaskSession)
        .filter(models.TaskSession.todo_id == todo.id)
        .count()
    )
    data = schemas.TodoResponse.model_validate(todo)
    data.session_count = session_count
    return data


@router.get("/", response_model=List[schemas.TodoResponse])
def list_todos(todo_list_id: Optional[int] = None, event_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Todo)
    if todo_list_id is not None:
        query = query.filter(models.Todo.todo_list_id == todo_list_id)
    if event_id is not None:
        query = query.filter(models.Todo.event_id == event_id)
    todos = query.order_by(models.Todo.created_at.desc()).all()
    return _enrich_todos(todos, db)


@router.get("/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return _enrich_todo(todo, db)


@router.post("/", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return _enrich_todo(db_todo, db)


@router.put("/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    for field, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, field, value)
    db.commit()
    db.refresh(db_todo)
    return _enrich_todo(db_todo, db)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(db_todo)
    db.commit()

