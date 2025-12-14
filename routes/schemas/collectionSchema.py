from typing import Optional
from sqlmodel import SQLModel
from datetime import date


class CollectionBase(SQLModel):
    name: str
    release_date: date


class CollectionCreate(CollectionBase):
    pass


class CollectionRead(CollectionBase):
    id: int


class CollectionUpdate(SQLModel):
    name: Optional[str] = None
    release_date: Optional[date] = None