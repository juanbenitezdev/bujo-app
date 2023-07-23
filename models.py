import datetime
import enum
from typing import Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    timezone = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, default=datetime.datetime.now)
    last_updated = Column(DateTime, onupdate=datetime.datetime.now)

    entries = relationship("Entry", back_populates="owner")
    projects = relationship("Project", back_populates="owner")


class EntryTypes(enum.IntEnum):
    BULLET = 1
    TASK = 2

    def __str__(self):
        return self.string


class EntryPriority(enum.IntEnum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    NONE = 9

    def __str__(self):
        return self.string


class IntEnum(TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).
    """
    impl = Integer

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, default="")
    priority = Column(Enum(EntryPriority), default=EntryPriority.NONE)
    due_date = Column(DateTime, nullable=True)
    completed = Column(DateTime, nullable=True)
    type = Column(Enum(EntryTypes), default=EntryTypes.TASK)
    created_on = Column(DateTime, default=datetime.datetime.now)
    last_updated = Column(DateTime, onupdate=datetime.datetime.now)

    # Sub Entries
    parent_entry_id: Mapped[Optional[int]] = mapped_column(ForeignKey("entries.id"))
    parent_entry = relationship("Entry", back_populates="child_entries", remote_side=[id])
    child_entries = relationship("Entry", back_populates="parent_entry")

    # Projects
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="entries")

    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="entries")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    created_on = Column(DateTime, default=datetime.datetime.now)
    last_updated = Column(DateTime, onupdate=datetime.datetime.now)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")

    entries = relationship("Entry", back_populates="project")
