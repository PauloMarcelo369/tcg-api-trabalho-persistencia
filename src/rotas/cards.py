from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models.models import Card, Collection, DeckCardLink

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.post("/")
def create_card(card: Card, session: Session = Depends(get_session)):
    """Cria um novo card"""
    # Verifica se a coleção existe
    collection = session.get(Collection, card.collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.get("/")
def list_cards(session: Session = Depends(get_session)):
    """Lista todos os cards"""
    cards = session.exec(select(Card)).all()
    return cards


@router.get("/{card_id}")
def get_card(card_id: int, session: Session = Depends(get_session)):
    """Obtém um card por ID"""
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card não encontrado")
    return card


@router.get("/collection/{collection_id}")
def get_cards_by_collection(collection_id: int, session: Session = Depends(get_session)):
    """Lista todos os cards de uma coleção"""
    collection = session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    
    cards = session.exec(select(Card).where(Card.collection_id == collection_id)).all()
    return cards


@router.put("/{card_id}")
def update_card(card_id: int, card_update: Card, session: Session = Depends(get_session)):
    """Atualiza um card"""
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card não encontrado")
    
    card_data = card_update.dict(exclude_unset=True)
    for key, value in card_data.items():
        setattr(card, key, value)
    
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.delete("/{card_id}")
def delete_card(card_id: int, session: Session = Depends(get_session)):
    """Deleta um card"""
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card não encontrado")
    
    session.delete(card)
    session.commit()
    return {"message": "Card deletado com sucesso"}


@router.post("/{deck_id}/cards/{card_id}")
def add_card_to_deck(deck_id: int, card_id: int, qty: int = 1, session: Session = Depends(get_session)):
    """Adiciona um card a um deck"""
    deck_card = DeckCardLink(deck_id=deck_id, card_id=card_id, qty=qty)
    session.add(deck_card)
    session.commit()
    return {"message": f"Card adicionado ao deck com quantidade {qty}"}


@router.delete("/{deck_id}/cards/{card_id}")
def remove_card_from_deck(deck_id: int, card_id: int, session: Session = Depends(get_session)):
    """Remove um card de um deck"""
    deck_card = session.exec(
        select(DeckCardLink).where(
            (DeckCardLink.deck_id == deck_id) & 
            (DeckCardLink.card_id == card_id)
        )
    ).first()
    
    if not deck_card:
        raise HTTPException(status_code=404, detail="Card não encontrado no deck")
    
    session.delete(deck_card)
    session.commit()
    return {"message": "Card removido do deck com sucesso"}
