from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from fastapi import APIRouter, HTTPException, depends, status, Query

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = field(index=True, unique=True, nullable=False)
    email: str = Field(default=None, index=True, unique=True)
    senha: str = Field(nullable=False)