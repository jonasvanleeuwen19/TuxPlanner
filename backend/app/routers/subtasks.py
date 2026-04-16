from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/events/{event_id}/subtasks", tags=["subtasks"])


def _get_event_or_404(event_id: int, db: Session) -> models.Event:
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("/", response_model=List[schemas.SubtaskResponse])
def list_subtasks(event_id: int, db: Session = Depends(get_db)):
    _get_event_or_404(event_id, db)
    return (
        db.query(models.Subtask)
        .filter(models.Subtask.event_id == event_id)
        .order_by(models.Subtask.created_at)
        .all()
    )


@router.post("/", response_model=schemas.SubtaskResponse, status_code=status.HTTP_201_CREATED)
def create_subtask(event_id: int, subtask: schemas.SubtaskCreate, db: Session = Depends(get_db)):
    _get_event_or_404(event_id, db)
    db_subtask = models.Subtask(**subtask.model_dump(), event_id=event_id)
    db.add(db_subtask)
    db.commit()
    db.refresh(db_subtask)
    return db_subtask


@router.put("/{subtask_id}", response_model=schemas.SubtaskResponse)
def update_subtask(event_id: int, subtask_id: int, subtask: schemas.SubtaskUpdate, db: Session = Depends(get_db)):
    _get_event_or_404(event_id, db)
    db_subtask = (
        db.query(models.Subtask)
        .filter(models.Subtask.id == subtask_id, models.Subtask.event_id == event_id)
        .first()
    )
    if not db_subtask:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtask not found")
    for field, value in subtask.model_dump(exclude_unset=True).items():
        setattr(db_subtask, field, value)
    db.commit()
    db.refresh(db_subtask)
    return db_subtask


@router.delete("/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subtask(event_id: int, subtask_id: int, db: Session = Depends(get_db)):
    _get_event_or_404(event_id, db)
    db_subtask = (
        db.query(models.Subtask)
        .filter(models.Subtask.id == subtask_id, models.Subtask.event_id == event_id)
        .first()
    )
    if not db_subtask:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtask not found")
    db.delete(db_subtask)
    db.commit()
