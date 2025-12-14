from typing import Optional
from sqlmodel import SQLModel
from datetime import datetime


class UserBase(SQLModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime


class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
