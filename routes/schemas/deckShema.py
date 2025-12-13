from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime
from models.models import DeckFormat
from routes.schemas.cardSchema import CardRead

class DeckBase(SQLModel):
    name : str
    format : DeckFormat
    user_id: int

class DeckCreate(DeckBase):
    pass

class DeckRead(DeckBase):
    id: int
    created_at: datetime

class DeckUpdate(SQLModel):
    name: Optional[str] = None
    format: Optional[DeckFormat] = None

class DeckWithCardsRead(SQLModel):
    id: int
    name: str
    format: DeckFormat
    cards: List[CardRead]