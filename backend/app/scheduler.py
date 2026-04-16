import datetime as dt_module
from datetime import datetime, timezone

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from icalendar import Calendar
from sqlalchemy.exc import IntegrityError
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


def _process_vevent(db: Session, feed: models.IcalFeed, component):
    """Process a single VEVENT component and upsert it into the DB."""
    _process_vevent_with_list(db, feed, component, feed.calendar_list_id)


def _process_vevent_with_list(db: Session, feed: models.IcalFeed, component, calendar_list_id):
    """Process a single VEVENT component and upsert it into the DB."""
    raw_uid = component.get("UID", "")
    uid = f"{feed.id}:{raw_uid}"
    if not raw_uid:
        return

    summary = str(component.get("SUMMARY", "Untitled"))
    description = _str_or_none(component.get("DESCRIPTION"))
    location = _str_or_none(component.get("LOCATION"))

    dtstart = component.get("DTSTART")
    dtend = component.get("DTEND")

    if dtstart is None:
        return

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
        existing.calendar_list_id = calendar_list_id
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
            calendar_list_id=calendar_list_id,
        ))


def _sync_ical(db: Session, feed: models.IcalFeed):
    """Sync an ICAL/webcal feed."""
    url = feed.url
    if url.startswith("webcal://"):
        url = "https://" + url[len("webcal://"):]
    elif url.startswith("webcals://"):
        url = "https://" + url[len("webcals://"):]
    with httpx.Client(follow_redirects=True, timeout=30) as client:
        response = client.get(url)
        response.raise_for_status()

    cal = Calendar.from_ical(response.content)
    for component in cal.walk():
        if component.name != "VEVENT":
            continue
        _process_vevent(db, feed, component)


def _get_or_create_caldav_calendar_list(
    db: Session, feed: models.IcalFeed, calendar_name: str
) -> models.CalendarList:
    """Return a CalendarList for a specific CalDAV calendar, creating it if needed."""
    cal_list = (
        db.query(models.CalendarList)
        .filter(
            models.CalendarList.ical_feed_id == feed.id,
            models.CalendarList.caldav_calendar_name == calendar_name,
        )
        .first()
    )
    if not cal_list:
        # Determine color: reuse the feed's primary list color if available
        primary = (
            db.query(models.CalendarList)
            .filter(models.CalendarList.id == feed.calendar_list_id)
            .first()
        ) if feed.calendar_list_id else None
        base_color = primary.color if primary else "#3b82f6"

        cal_list = models.CalendarList(
            name=f"{feed.name}: {calendar_name}",
            color=base_color,
            ical_feed_id=feed.id,
            caldav_calendar_name=calendar_name,
            is_visible=True,
        )
        db.add(cal_list)
        try:
            db.commit()
            db.refresh(cal_list)
        except IntegrityError:
            # Another process/iteration already inserted a matching row; roll back
            # and re-query to get the existing record.
            db.rollback()
            cal_list = (
                db.query(models.CalendarList)
                .filter(
                    models.CalendarList.ical_feed_id == feed.id,
                    models.CalendarList.caldav_calendar_name == calendar_name,
                )
                .first()
            )
            if cal_list is None:
                raise RuntimeError(
                    f"Failed to get or create CalendarList for feed {feed.id} "
                    f"calendar '{calendar_name}'"
                )
    return cal_list


def _sync_caldav(db: Session, feed: models.IcalFeed):
    """Sync a CalDAV calendar feed."""
    import caldav

    client = caldav.DAVClient(
        url=feed.url,
        username=feed.caldav_username or "",
        password=feed.caldav_password or "",
    )
    principal = client.principal()
    calendars = principal.calendars()

    for calendar in calendars:
        try:
            cal_name = str(calendar.name) if calendar.name else "Calendar"
        except Exception:
            cal_name = "Calendar"

        cal_list = _get_or_create_caldav_calendar_list(db, feed, cal_name)

        events = calendar.events()
        for event in events:
            try:
                cal = Calendar.from_ical(event.data)
                for component in cal.walk():
                    if component.name != "VEVENT":
                        continue
                    _process_vevent_with_list(db, feed, component, cal_list.id)
            except Exception as e:
                print(f"CalDAV event parse error for feed {feed.id}: {e}")


def _sync_feed(db: Session, feed: models.IcalFeed):
    try:
        feed_type = getattr(feed, "feed_type", "ical") or "ical"
        if feed_type == "caldav":
            _sync_caldav(db, feed)
        else:
            _sync_ical(db, feed)

        feed.last_synced = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        print(f"Feed sync failed for feed {feed.id}: {e}")
        db.rollback()


def start_scheduler():
    scheduler.add_job(sync_all_ical_feeds, "interval", hours=1, id="ical_hourly_sync", replace_existing=True)
    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
