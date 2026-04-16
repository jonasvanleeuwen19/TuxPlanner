import datetime as dt_module
from datetime import datetime, timezone

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from icalendar import Calendar
from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal

scheduler = BackgroundScheduler()


def sync_feed_by_id(feed_id: int):
    db = SessionLocal()
    try:
        feed = db.query(models.IcalFeed).filter(models.IcalFeed.id == feed_id).first()
        if feed:
            _sync_feed(db, feed)
    finally:
        db.close()


def sync_all_ical_feeds():
    db = SessionLocal()
    try:
        feeds = db.query(models.IcalFeed).filter(models.IcalFeed.is_active.is_(True)).all()
        for feed in feeds:
            _sync_feed(db, feed)
    finally:
        db.close()


def _str_or_none(value):
    return str(value) if value else None


def _sync_feed(db: Session, feed: models.IcalFeed):
    try:
        with httpx.Client(follow_redirects=True, timeout=30) as client:
            response = client.get(feed.url)
            response.raise_for_status()

        cal = Calendar.from_ical(response.content)

        for component in cal.walk():
            if component.name != "VEVENT":
                continue

            raw_uid = component.get("UID", "")
            uid = f"{feed.id}:{raw_uid}"
            if not raw_uid:
                continue

            summary = str(component.get("SUMMARY", "Untitled"))
            description = _str_or_none(component.get("DESCRIPTION"))
            location = _str_or_none(component.get("LOCATION"))

            dtstart = component.get("DTSTART")
            dtend = component.get("DTEND")

            if dtstart is None:
                continue

            start_dt = dtstart.dt
            end_dt = dtend.dt if dtend else None

            all_day = isinstance(start_dt, dt_module.date) and not isinstance(start_dt, dt_module.datetime)

            if all_day:
                start_dt = datetime(start_dt.year, start_dt.month, start_dt.day, tzinfo=timezone.utc)
                if end_dt and isinstance(end_dt, dt_module.date) and not isinstance(end_dt, dt_module.datetime):
                    end_dt = datetime(end_dt.year, end_dt.month, end_dt.day, tzinfo=timezone.utc)
            else:
                if isinstance(start_dt, dt_module.datetime) and start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
                if end_dt and isinstance(end_dt, dt_module.datetime) and end_dt.tzinfo is None:
                    end_dt = end_dt.replace(tzinfo=timezone.utc)

            existing = db.query(models.Event).filter(
                models.Event.ical_uid == uid,
                models.Event.source == "ical",
            ).first()

            if existing:
                existing.title = summary
                existing.description = description
                existing.location = location
                existing.start = start_dt
                existing.end = end_dt
                existing.all_day = all_day
            else:
                db.add(models.Event(
                    title=summary,
                    description=description,
                    location=location,
                    start=start_dt,
                    end=end_dt,
                    all_day=all_day,
                    source="ical",
                    ical_uid=uid,
                ))

        feed.last_synced = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        print(f"ICAL sync failed for feed {feed.id}: {e}")
        db.rollback()


def start_scheduler():
    scheduler.add_job(sync_all_ical_feeds, "interval", hours=1, id="ical_hourly_sync", replace_existing=True)
    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
