from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models.models import Deck, DeckCardLink, Card
from routes.schemas.deckShema import DeckCreate, DeckRead, DeckUpdate

router = APIRouter(prefix="/decks", tags=["Decks"])

from pydantic import ValidationError

@router.post("/", response_model=DeckRead)
def create_deck(data: DeckCreate, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Deck).where(
            (Deck.name == data.name) & (Deck.user_id == data.user_id)
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Usuário já tem deck com esse nome!"
        )
    try:
        deck = Deck.model_validate(data)
        session.add(deck)
        session.commit()
        session.refresh(deck)
        return deck

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao criar deck!")