from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/events", tags=["events"])


def _enrich_event(event: models.Event, db: Session) -> schemas.EventResponse:
    """Build an EventResponse, adding subtask_category_names."""
    subtasks = (
        db.query(models.Subtask)
        .filter(models.Subtask.event_id == event.id)
        .all()
    )
    cat_ids = {s.category_id for s in subtasks if s.category_id}
    cat_names: List[str] = []
    if cat_ids:
        cats = db.query(models.SubtaskCategory).filter(models.SubtaskCategory.id.in_(cat_ids)).all()
        cat_names = sorted({c.name for c in cats})
    data = schemas.EventResponse.model_validate(event)
    data.subtask_category_names = cat_names
    return data


def _enrich_events(events: list, db: Session) -> List[schemas.EventResponse]:
    """Batch-enrich a list of events with subtask category names."""
    if not events:
        return []
    event_ids = [e.id for e in events]
    subtasks = (
        db.query(models.Subtask)
        .filter(models.Subtask.event_id.in_(event_ids))
        .all()
    )
    # Build mapping: event_id -> set of category_ids
    event_cats: dict = {e.id: set() for e in events}
    cat_ids_needed: set = set()
    for s in subtasks:
        if s.category_id:
            event_cats[s.event_id].add(s.category_id)
            cat_ids_needed.add(s.category_id)
    # Fetch all needed categories
    cat_map: dict = {}
    if cat_ids_needed:
        cats = db.query(models.SubtaskCategory).filter(models.SubtaskCategory.id.in_(cat_ids_needed)).all()
        cat_map = {c.id: c.name for c in cats}
    results = []
    for event in events:
        data = schemas.EventResponse.model_validate(event)
        data.subtask_category_names = sorted({cat_map[cid] for cid in event_cats[event.id] if cid in cat_map})
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
