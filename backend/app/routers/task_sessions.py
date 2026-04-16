from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/todos", tags=["task-sessions"])

PLANNED_TASKS_LIST_NAME = "Planned Tasks"
PLANNED_TASKS_LIST_COLOR = "#8b5cf6"


def _get_or_create_planned_tasks_list(db: Session) -> models.CalendarList:
    """Return the 'Planned Tasks' calendar list, creating it if it does not exist."""
    cal_list = (
        db.query(models.CalendarList)
        .filter(models.CalendarList.name == PLANNED_TASKS_LIST_NAME)
        .first()
    )
    if not cal_list:
        cal_list = models.CalendarList(
            name=PLANNED_TASKS_LIST_NAME,
            color=PLANNED_TASKS_LIST_COLOR,
            is_visible=True,
        )
        db.add(cal_list)
        db.commit()
        db.refresh(cal_list)
    return cal_list


def _build_session_event_title(todo: models.Todo) -> str:
    return f"📋 Work on: {todo.title}"


def _build_session_event_description(todo: models.Todo, note: str | None) -> str:
    parts = [f"Task session for: {todo.title}"]
    if note:
        parts.append(note)
    return "\n\n".join(parts)


@router.get("/{todo_id}/sessions/", response_model=List[schemas.TaskSessionResponse])
def list_sessions(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return (
        db.query(models.TaskSession)
        .filter(models.TaskSession.todo_id == todo_id)
        .order_by(models.TaskSession.start)
        .all()
    )


@router.post("/{todo_id}/sessions/", response_model=schemas.TaskSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(todo_id: int, session_data: schemas.TaskSessionCreate, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    cal_list = _get_or_create_planned_tasks_list(db)

    # Create a calendar event for this session
    cal_event = models.Event(
        title=_build_session_event_title(todo),
        description=_build_session_event_description(todo, session_data.note),
        start=session_data.start,
        end=session_data.end,
        all_day=False,
        source="task_session",
        calendar_list_id=cal_list.id,
        color=PLANNED_TASKS_LIST_COLOR,
    )
    db.add(cal_event)
    db.flush()  # get cal_event.id without committing

    task_session = models.TaskSession(
        todo_id=todo_id,
        event_id=cal_event.id,
        start=session_data.start,
        end=session_data.end,
        note=session_data.note,
    )
    db.add(task_session)
    db.commit()
    db.refresh(task_session)
    return task_session


@router.put("/{todo_id}/sessions/{session_id}", response_model=schemas.TaskSessionResponse)
def update_session(todo_id: int, session_id: int, session_data: schemas.TaskSessionUpdate, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    task_session = (
        db.query(models.TaskSession)
        .filter(models.TaskSession.id == session_id, models.TaskSession.todo_id == todo_id)
        .first()
    )
    if not task_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    update_fields = session_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(task_session, field, value)

    # Keep the linked calendar event in sync
    if task_session.event_id:
        cal_event = db.query(models.Event).filter(models.Event.id == task_session.event_id).first()
        if cal_event:
            if "start" in update_fields:
                cal_event.start = task_session.start
            if "end" in update_fields:
                cal_event.end = task_session.end
            if "note" in update_fields:
                cal_event.description = _build_session_event_description(todo, task_session.note)

    db.commit()
    db.refresh(task_session)
    return task_session


@router.delete("/{todo_id}/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(todo_id: int, session_id: int, db: Session = Depends(get_db)):
    task_session = (
        db.query(models.TaskSession)
        .filter(models.TaskSession.id == session_id, models.TaskSession.todo_id == todo_id)
        .first()
    )
    if not task_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Delete the associated calendar event
    if task_session.event_id:
        cal_event = db.query(models.Event).filter(models.Event.id == task_session.event_id).first()
        if cal_event:
            db.delete(cal_event)

    db.delete(task_session)
    db.commit()
