from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from src.database import get_session
from models.models import Deck, DeckCardLink, Card
from schemas.deckShema import DeckCreate, DeckRead, DeckUpdate

router = APIRouter(prefix="/decks")