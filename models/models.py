from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Deck, Card, Collection, User

# enums para o tipo de carta e raridade dela
class CardType(str, Enum):
    Dragon = "Dragon"
    Warrior = "Warrior"
    Magician = "Magician"
    Dinosaur = "Dinosaur"
    Spell = "Spell"
    Mage = "Mage"

class CardRarity(str, Enum):
    Common = "Common"
    Uncommon = "Uncommon"
    Rare = "Rare"
    Mythic = "Mythic"


#tipo de formato para o deck
class DeckFormat(str, Enum):
    Standard = "Standard"
    Modern = "Modern"
    Commander = "Commander"
    Pauper = "Pauper"

#Aqui a tabela de cards do deck (many-to-many) que precisamos :)
class DeckCardLink(SQLModel, table=True):
    deck_id: Optional[int] = Field(default=None, foreign_key="deck.id", primary_key=True)
    card_id: Optional[int] = Field(default=None, foreign_key="card.id", primary_key=True)
    qty: int = Field(default=1, ge=1, le=3)

# aqui temos a coleção em que as cartas vem
class Collection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name : str = Field(nullable=False, unique=True)
    release_date: date = Field(nullable=False)
    cards: List["Card"] = Relationship(back_populates="collection")

#aqui temos a representação do card proprieamente dito
class Card(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name : str = Field(nullable=False, unique=True)
    type: CardType = Field(nullable=False)
    rarity: CardRarity = Field(nullable=False)
    text: Optional[str] = Field(default=None)
    collection_id: int = Field(foreign_key="collection.id", nullable=False)
    collection : Collection = Relationship(back_populates="cards")
    decks: List["Deck"] = Relationship(back_populates="cards", link_model=DeckCardLink)

#aqui fazemos a table do User (dono dos decks)
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name : str = Field(nullable=False)
    email : str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    decks : List["Deck"] = Relationship(back_populates="owner")

#
class Deck(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name : str = Field(nullable=False)
    format: DeckFormat = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="decks")
    cards : List[Card] = Relationship(back_populates="decks", link_model=DeckCardLink)