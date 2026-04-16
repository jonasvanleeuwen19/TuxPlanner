from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# ── Calendar List ────────────────────────────────────────────


class CalendarListBase(BaseModel):
    name: str
    color: str = "#3b82f6"
    is_visible: bool = True


class CalendarListCreate(CalendarListBase):
    pass


class CalendarListUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    is_visible: Optional[bool] = None


class CalendarListResponse(CalendarListBase):
    id: int
    ical_feed_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Event ─────────────────────────────────────────────────────


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start: datetime
    end: Optional[datetime] = None
    all_day: bool = False
    color: Optional[str] = None
    calendar_list_id: Optional[int] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    all_day: Optional[bool] = None
    color: Optional[str] = None
    calendar_list_id: Optional[int] = None


class EventResponse(EventBase):
    id: int
    source: Optional[str] = None
    ical_uid: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    subtask_category_names: List[str] = []

    class Config:
        from_attributes = True


# ── Todo List ─────────────────────────────────────────────────


class TodoListBase(BaseModel):
    name: str
    color: str = "#3b82f6"


class TodoListCreate(TodoListBase):
    pass


class TodoListUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TodoListResponse(TodoListBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    due_date: Optional[datetime] = None
    todo_list_id: Optional[int] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    todo_list_id: Optional[int] = None


class TodoResponse(TodoBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IcalFeedBase(BaseModel):
    name: str
    url: str
    is_active: bool = True


class IcalFeedCreate(IcalFeedBase):
    color: str = "#3b82f6"


class IcalFeedUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None


class IcalFeedResponse(IcalFeedBase):
    id: int
    last_synced: Optional[datetime] = None
    created_at: datetime
    calendar_list_id: Optional[int] = None

    class Config:
        from_attributes = True


# ── Subtask Category ──────────────────────────────────────────


class SubtaskCategoryBase(BaseModel):
    name: str


class SubtaskCategoryCreate(SubtaskCategoryBase):
    pass


class SubtaskCategoryUpdate(BaseModel):
    name: Optional[str] = None


class SubtaskCategoryResponse(SubtaskCategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Subtask ───────────────────────────────────────────────────


class SubtaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    completed: bool = False


class SubtaskCreate(SubtaskBase):
    pass


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    completed: Optional[bool] = None


class SubtaskResponse(SubtaskBase):
    id: int
    event_id: int
    created_at: datetime

    class Config:
        from_attributes = True
