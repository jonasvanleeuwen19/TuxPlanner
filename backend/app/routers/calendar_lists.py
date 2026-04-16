from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/calendar-lists", tags=["calendar-lists"])


@router.get("/", response_model=List[schemas.CalendarListResponse])
def list_calendar_lists(db: Session = Depends(get_db)):
    return db.query(models.CalendarList).order_by(models.CalendarList.created_at).all()


@router.get("/{list_id}", response_model=schemas.CalendarListResponse)
def get_calendar_list(list_id: int, db: Session = Depends(get_db)):
    cal_list = db.query(models.CalendarList).filter(models.CalendarList.id == list_id).first()
    if not cal_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar list not found")
    return cal_list


@router.post("/", response_model=schemas.CalendarListResponse, status_code=status.HTTP_201_CREATED)
def create_calendar_list(cal_list: schemas.CalendarListCreate, db: Session = Depends(get_db)):
    db_list = models.CalendarList(**cal_list.model_dump())
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


@router.put("/{list_id}", response_model=schemas.CalendarListResponse)
def update_calendar_list(list_id: int, cal_list: schemas.CalendarListUpdate, db: Session = Depends(get_db)):
    db_list = db.query(models.CalendarList).filter(models.CalendarList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar list not found")
    for field, value in cal_list.model_dump(exclude_unset=True).items():
        setattr(db_list, field, value)
    db.commit()
    db.refresh(db_list)
    return db_list


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar_list(list_id: int, db: Session = Depends(get_db)):
    db_list = db.query(models.CalendarList).filter(models.CalendarList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar list not found")
    if db_list.ical_feed_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete an ICAL-linked calendar list directly. Delete the ICAL feed instead.",
        )
    db.query(models.Event).filter(models.Event.calendar_list_id == list_id).update(
        {models.Event.calendar_list_id: None}
    )
    db.delete(db_list)
    db.commit()
