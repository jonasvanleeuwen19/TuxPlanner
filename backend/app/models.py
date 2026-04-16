from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class CalendarList(Base):
    __tablename__ = "calendar_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    color = Column(String(50), nullable=False, default="#3b82f6")
    is_visible = Column(Boolean, default=True)
    ical_feed_id = Column(Integer, ForeignKey("ical_feeds.id", ondelete="CASCADE"), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    start = Column(DateTime(timezone=True), nullable=False)
    end = Column(DateTime(timezone=True), nullable=True)
    all_day = Column(Boolean, default=False)
    color = Column(String(50), nullable=True)
    source = Column(String(50), nullable=True)
    ical_uid = Column(String(500), nullable=True, index=True)
    calendar_list_id = Column(Integer, ForeignKey("calendar_lists.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String(20), default="medium")
    due_date = Column(DateTime(timezone=True), nullable=True)
    todo_list_id = Column(Integer, ForeignKey("todo_lists.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IcalFeed(Base):
    __tablename__ = "ical_feeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    last_synced = Column(DateTime(timezone=True), nullable=True)
    # calendar_list_id is stored as a plain integer (no FK constraint) to avoid a
    # circular foreign-key cycle with calendar_lists.ical_feed_id → ical_feeds.id.
    # Application logic in the ical_feeds router enforces the relationship.
    calendar_list_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SubtaskCategory(Base):
    __tablename__ = "subtask_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TodoList(Base):
    __tablename__ = "todo_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    color = Column(String(50), nullable=False, default="#3b82f6")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("subtask_categories.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
