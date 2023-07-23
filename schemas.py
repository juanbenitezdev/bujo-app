import datetime
from typing import Optional, ForwardRef

from pydantic import BaseModel
from models import EntryTypes, EntryPriority

Entry = ForwardRef('Entry')


class ProjectBase(BaseModel):
    title: str


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    created_on: datetime.datetime
    last_updated: Optional[datetime.datetime]

    owner_id: int

    entries: list[Entry] = []

    class Config:
        orm_mode = True


class ProjectNotEntries(ProjectBase):
    id: int

    class Config:
        orm_mode = True


class EntryBase(BaseModel):
    title: str
    type: EntryTypes
    priority: EntryPriority
    due_date: Optional[datetime.datetime]


class EntryCreate(EntryBase):
    project_id: int
    parent_entry_id: Optional[int]


class Entry(EntryBase):
    id: int
    created_on: datetime.datetime
    last_updated: Optional[datetime.datetime]
    completed: Optional[datetime.datetime]

    project: ProjectNotEntries
    child_entries: list[Entry] = []

    owner_id: int

    class Config:
        orm_mode = True
        json_encoders = {
            EntryTypes: lambda x: x.name,
            EntryPriority: lambda x: x.name,
        }


class EntryNotTask(EntryBase):
    id: int
    created_on: datetime.datetime
    last_updated: Optional[datetime.datetime]

    owner_id: int

    class Config:
        orm_mode = True


Entry.update_forward_refs()


class UserBase(BaseModel):
    name: str
    email: str
    timezone: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_on: datetime.datetime
    last_updated: Optional[datetime.datetime]

    entries: list[Entry] = []
    projects: list[ProjectNotEntries] = []

    class Config:
        orm_mode = True


Project.update_forward_refs()
