from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/todo-lists", tags=["todo-lists"])


@router.get("/", response_model=List[schemas.TodoListResponse])
def list_todo_lists(db: Session = Depends(get_db)):
    return db.query(models.TodoList).order_by(models.TodoList.created_at).all()


@router.get("/{list_id}", response_model=schemas.TodoListResponse)
def get_todo_list(list_id: int, db: Session = Depends(get_db)):
    todo_list = db.query(models.TodoList).filter(models.TodoList.id == list_id).first()
    if not todo_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo list not found")
    return todo_list


@router.post("/", response_model=schemas.TodoListResponse, status_code=status.HTTP_201_CREATED)
def create_todo_list(todo_list: schemas.TodoListCreate, db: Session = Depends(get_db)):
    db_list = models.TodoList(**todo_list.model_dump())
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


@router.put("/{list_id}", response_model=schemas.TodoListResponse)
def update_todo_list(list_id: int, todo_list: schemas.TodoListUpdate, db: Session = Depends(get_db)):
    db_list = db.query(models.TodoList).filter(models.TodoList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo list not found")
    for field, value in todo_list.model_dump(exclude_unset=True).items():
        setattr(db_list, field, value)
    db.commit()
    db.refresh(db_list)
    return db_list


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_list(list_id: int, db: Session = Depends(get_db)):
    db_list = db.query(models.TodoList).filter(models.TodoList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo list not found")
    # Unlink todos from this list instead of deleting them
    db.query(models.Todo).filter(models.Todo.todo_list_id == list_id).update(
        {models.Todo.todo_list_id: None}
    )
    db.delete(db_list)
    db.commit()
