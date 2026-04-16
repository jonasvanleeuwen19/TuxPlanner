from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/events", tags=["events"])


def _enrich_event(event: models.Event, db: Session) -> schemas.EventResponse:
    """Build an EventResponse, adding task_count (linked todos)."""
    task_count = (
        db.query(models.Todo)
        .filter(models.Todo.event_id == event.id)
        .count()
    )
    data = schemas.EventResponse.model_validate(event)
    data.task_count = task_count
    return data


def _enrich_events(events: list, db: Session) -> List[schemas.EventResponse]:
    """Batch-enrich a list of events with task_count (linked todos)."""
    if not events:
        return []
    event_ids = [e.id for e in events]
    todos = (
        db.query(models.Todo.event_id)
        .filter(models.Todo.event_id.in_(event_ids))
        .all()
    )
    # Build mapping: event_id -> count
    count_map: dict = {e.id: 0 for e in events}
    for (eid,) in todos:
        if eid in count_map:
            count_map[eid] += 1
    results = []
    for event in events:
        data = schemas.EventResponse.model_validate(event)
        data.task_count = count_map.get(event.id, 0)
        results.append(data)
    return results


@router.get("/", response_model=List[schemas.EventResponse])
def list_events(
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Event)
    if start:
        query = query.filter(models.Event.start >= start)
    if end:
        query = query.filter(models.Event.start <= end)
    events = query.order_by(models.Event.start).all()
    return _enrich_events(events, db)


@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return _enrich_event(event, db)


@router.post("/", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return _enrich_event(db_event, db)


@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db)):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    for field, value in event.model_dump(exclude_unset=True).items():
        setattr(db_event, field, value)
    db.commit()
    db.refresh(db_event)
    return _enrich_event(db_event, db)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if db_event.source == "ical":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ICAL events cannot be deleted manually")
    db.delete(db_event)
    db.commit()
