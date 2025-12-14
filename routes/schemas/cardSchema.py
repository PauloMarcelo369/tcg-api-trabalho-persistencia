from typing import Optional
from sqlmodel import SQLModel
from models.models import CardType, CardRarity


class CardBase(SQLModel):
    name: str
    type: CardType
    rarity: CardRarity
    text: Optional[str] = None
    collection_id: int


class CardCreate(CardBase):
    pass


class CardRead(CardBase):
    id: int


class CardUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[CardType] = None
    rarity: Optional[CardRarity] = None
    text: Optional[str] = None
    collection_id: Optional[int] = None
