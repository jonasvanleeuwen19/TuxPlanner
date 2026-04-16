from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/ical-feeds", tags=["ical-feeds"])


@router.get("/", response_model=List[schemas.IcalFeedResponse])
def list_feeds(db: Session = Depends(get_db)):
    return db.query(models.IcalFeed).order_by(models.IcalFeed.created_at.desc()).all()


@router.get("/{feed_id}", response_model=schemas.IcalFeedResponse)
def get_feed(feed_id: int, db: Session = Depends(get_db)):
    feed = db.query(models.IcalFeed).filter(models.IcalFeed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")
    return feed


@router.post("/", response_model=schemas.IcalFeedResponse, status_code=status.HTTP_201_CREATED)
def create_feed(feed: schemas.IcalFeedCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_feed = models.IcalFeed(**feed.model_dump())
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    background_tasks.add_task(sync_single_feed, db_feed.id)
    return db_feed


@router.put("/{feed_id}", response_model=schemas.IcalFeedResponse)
def update_feed(feed_id: int, feed: schemas.IcalFeedUpdate, db: Session = Depends(get_db)):
    db_feed = db.query(models.IcalFeed).filter(models.IcalFeed.id == feed_id).first()
    if not db_feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")
    for field, value in feed.model_dump(exclude_unset=True).items():
        setattr(db_feed, field, value)
    db.commit()
    db.refresh(db_feed)
    return db_feed


@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feed(feed_id: int, db: Session = Depends(get_db)):
    db_feed = db.query(models.IcalFeed).filter(models.IcalFeed.id == feed_id).first()
    if not db_feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")
    db.query(models.Event).filter(
        models.Event.source == "ical",
        models.Event.ical_uid.like(f"{db_feed.id}:%"),
    ).delete(synchronize_session=False)
    db.delete(db_feed)
    db.commit()


@router.post("/{feed_id}/sync", response_model=schemas.IcalFeedResponse)
def sync_feed_now(feed_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_feed = db.query(models.IcalFeed).filter(models.IcalFeed.id == feed_id).first()
    if not db_feed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")
    background_tasks.add_task(sync_single_feed, feed_id)
    return db_feed


def sync_single_feed(feed_id: int):
    from app.scheduler import sync_feed_by_id
    sync_feed_by_id(feed_id)
