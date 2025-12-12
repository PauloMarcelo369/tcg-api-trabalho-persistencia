from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models.models import Deck, User

router = APIRouter(prefix="/decks", tags=["Decks"])


@router.post("/")
def create_deck(deck: Deck, session: Session = Depends(get_session)):
    """Cria um novo deck"""
    # Verifica se o usuário existe
    user = session.get(User, deck.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    session.add(deck)
    session.commit()
    session.refresh(deck)
    return deck


@router.get("/")
def list_decks(session: Session = Depends(get_session)):
    """Lista todos os decks"""
    decks = session.exec(select(Deck)).all()
    return decks


@router.get("/{deck_id}")
def get_deck(deck_id: int, session: Session = Depends(get_session)):
    """Obtém um deck por ID"""
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck não encontrado")
    return deck


@router.get("/user/{user_id}")
def get_user_decks(user_id: int, session: Session = Depends(get_session)):
    """Lista todos os decks de um usuário"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    decks = session.exec(select(Deck).where(Deck.user_id == user_id)).all()
    return decks


@router.put("/{deck_id}")
def update_deck(deck_id: int, deck_update: Deck, session: Session = Depends(get_session)):
    """Atualiza um deck"""
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck não encontrado")
    
    deck_data = deck_update.dict(exclude_unset=True)
    for key, value in deck_data.items():
        setattr(deck, key, value)
    
    session.add(deck)
    session.commit()
    session.refresh(deck)
    return deck


@router.delete("/{deck_id}")
def delete_deck(deck_id: int, session: Session = Depends(get_session)):
    """Deleta um deck"""
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck não encontrado")
    
    session.delete(deck)
    session.commit()
    return {"message": "Deck deletado com sucesso"}
