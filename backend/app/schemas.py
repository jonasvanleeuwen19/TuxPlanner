from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start: datetime
    end: Optional[datetime] = None
    all_day: bool = False
    color: Optional[str] = None


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


class EventResponse(EventBase):
    id: int
    source: Optional[str] = None
    ical_uid: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    due_date: Optional[datetime] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


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
    pass


class IcalFeedUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    is_active: Optional[bool] = None


class IcalFeedResponse(IcalFeedBase):
    id: int
    last_synced: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
