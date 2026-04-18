from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.auth import get_current_user
from app.database import Base, engine
from app.routers import events, todos
from app.routers import auth, ical_feeds, calendar_lists, subtask_categories, subtasks, todo_lists, task_sessions
from app.scheduler import start_scheduler, stop_scheduler

Base.metadata.create_all(bind=engine)


def run_migrations():
    """Add missing columns to existing tables without dropping data."""
    migrations = [
        "ALTER TABLE events ADD COLUMN IF NOT EXISTS location VARCHAR(500)",
        "ALTER TABLE events ADD COLUMN IF NOT EXISTS color VARCHAR(50)",
        "ALTER TABLE events ADD COLUMN IF NOT EXISTS source VARCHAR(50)",
        "ALTER TABLE events ADD COLUMN IF NOT EXISTS ical_uid VARCHAR(500)",
        "ALTER TABLE events ADD COLUMN IF NOT EXISTS all_day BOOLEAN DEFAULT FALSE",
        "ALTER TABLE todos ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium'",
        "ALTER TABLE todos ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE events ADD COLUMN IF NOT EXISTS calendar_list_id INTEGER",
        "ALTER TABLE ical_feeds ADD COLUMN IF NOT EXISTS calendar_list_id INTEGER",
        # New migrations
        "ALTER TABLE subtasks ADD COLUMN IF NOT EXISTS description TEXT",
        "ALTER TABLE todos ADD COLUMN IF NOT EXISTS todo_list_id INTEGER",
        "ALTER TABLE todos ADD COLUMN IF NOT EXISTS category VARCHAR(255) DEFAULT 'Default'",
        "UPDATE todos SET category = 'Default' WHERE category IS NULL",
        "ALTER TABLE ical_feeds ADD COLUMN IF NOT EXISTS feed_type VARCHAR(20) DEFAULT 'ical'",
        "UPDATE ical_feeds SET feed_type = 'ical' WHERE feed_type IS NULL",
        "ALTER TABLE ical_feeds ADD COLUMN IF NOT EXISTS caldav_username VARCHAR(255)",
        "ALTER TABLE ical_feeds ADD COLUMN IF NOT EXISTS caldav_password TEXT",
        "ALTER TABLE todos ADD COLUMN IF NOT EXISTS event_id INTEGER",
        # Task sessions
        """CREATE TABLE IF NOT EXISTS task_sessions (
            id SERIAL PRIMARY KEY,
            todo_id INTEGER NOT NULL REFERENCES todos(id) ON DELETE CASCADE,
            event_id INTEGER REFERENCES events(id) ON DELETE SET NULL,
            start TIMESTAMP WITH TIME ZONE NOT NULL,
            "end" TIMESTAMP WITH TIME ZONE,
            note TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )""",
        # Calendar list enhancements
        "ALTER TABLE calendar_lists ADD COLUMN IF NOT EXISTS is_auto BOOLEAN DEFAULT FALSE",
        "ALTER TABLE calendar_lists ADD COLUMN IF NOT EXISTS caldav_calendar_name VARCHAR(255)",
        # Update existing Planned Tasks list to be auto
        "UPDATE calendar_lists SET is_auto = TRUE WHERE name = 'Planned Tasks' AND is_auto IS NOT TRUE",
        # Drop the single-column unique constraint on ical_feed_id so that one CalDAV
        # feed can have multiple CalendarList rows (one per remote calendar).
        "ALTER TABLE calendar_lists DROP CONSTRAINT IF EXISTS calendar_lists_ical_feed_id_key",
        # Replace it with a composite unique index covering (ical_feed_id, caldav_calendar_name)
        # to still prevent accidental duplicates for the same CalDAV calendar.
        """CREATE UNIQUE INDEX IF NOT EXISTS uq_calendar_lists_ical_feed_caldav_name
               ON calendar_lists (ical_feed_id, caldav_calendar_name)
               WHERE caldav_calendar_name IS NOT NULL""",
        # Users table for first-run account setup
        """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )""",
    ]
    with engine.begin() as conn:
        for stmt in migrations:
            conn.execute(text(stmt))


run_migrations()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="TuxPlanner API",
    description="Backend API for the TuxPlanner self-hosted calendar app",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")

_protected = {"dependencies": [Depends(get_current_user)]}
app.include_router(events.router, prefix="/api", **_protected)
app.include_router(todos.router, prefix="/api", **_protected)
app.include_router(ical_feeds.router, prefix="/api", **_protected)
app.include_router(calendar_lists.router, prefix="/api", **_protected)
app.include_router(subtask_categories.router, prefix="/api", **_protected)
app.include_router(subtasks.router, prefix="/api", **_protected)
app.include_router(todo_lists.router, prefix="/api", **_protected)
app.include_router(task_sessions.router, prefix="/api", **_protected)


@app.get("/")
def root():
    return {"message": "TuxPlanner API is running", "docs": "/docs"}
