from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from database import get_session
from models.models import Deck, DeckCardLink, Card, DeckFormat
from routes.schemas.deckShema import DeckCreate, DeckRead, DeckUpdate

router = APIRouter(prefix="/decks", tags=["Decks"])

from pydantic import ValidationError

@router.post("/", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def create_deck(data: DeckCreate, session: Session = Depends(get_session)):
    """Create a new user deck"""
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


@router.get("/{deck_id}", response_model=DeckRead,status_code=status.HTTP_200_OK)
def get_deck_by_id(deck_id : int, session: Session = Depends(get_session)):
    """Get Deck by ID"""
    deck = session.get(Deck, deck_id)
    if (not deck):
        raise HTTPException(404, f"Deck com ID {deck_id} não existe!")
    return deck


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck_by_id(deck_id: int, session: Session = Depends(get_session)):
    """Delete a Deck"""
    deck = session.get(Deck, deck_id)
    if (not deck):
        raise HTTPException(404, f"Deck com ID {deck_id} não existe!")

    try:
        session.delete(deck)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(400, f"Houve um problema ao deletar o Deck com ID {deck_id}!")
    

@router.put("/{deck_id}", response_model=DeckRead, status_code=status.HTTP_200_OK)
def put(deck_id : int, updated_deck : DeckUpdate,  session: Session = Depends(get_session)):
    deck = session.get(Deck, deck_id)

    if (not deck):
        raise HTTPException(404, f"Deck com ID {deck_id} não existe!")

    deck_dict = updated_deck.model_dump(exclude_unset=True)
    if not deck_dict:
        raise HTTPException(400, "Nenhum campo para atualizar")
    
    try:
        for key, value in deck_dict.items():
            setattr(deck, key, value)
        session.commit()
        session.refresh(deck)
        return deck
    
    except Exception as e:
        session.rollback()
        raise HTTPException(400, f"Não foi posssível atualizar Deck com ID {deck_id}!")
