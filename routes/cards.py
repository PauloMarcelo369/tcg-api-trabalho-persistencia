from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlmodel import Session, select
from database import get_session
from models.models import Card
from routes.schemas.cardSchema import CardCreate, CardRead, CardUpdate
from pydantic import ValidationError


router = APIRouter(prefix="/cards", tags=["Cards"])


@router.post("/", response_model=CardRead, status_code=status.HTTP_201_CREATED)
def create_card(data: CardCreate, session: Session = Depends(get_session)):
    """Create a new card"""
    existing = session.exec(select(Card).where(Card.name == data.name)).first()

    if existing:
        raise HTTPException(status_code=400, detail="Carta com esse nome já existe!")

    try:
        card = Card.model_validate(data)
        session.add(card)
        session.commit()
        session.refresh(card)
        return card

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao criar carta!")


@router.get("/{card_id}", response_model=CardRead, status_code=status.HTTP_200_OK)
def get_card_by_id(card_id: int, session: Session = Depends(get_session)):
    """Get Card by ID"""
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(404, f"Carta com ID {card_id} não existe!")
    return card


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card_by_id(card_id: int, session: Session = Depends(get_session)):
    """Delete a Card"""
    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(404, f"Carta com ID {card_id} não existe!")

    try:
        session.delete(card)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(400, f"Houve um problema ao deletar a Carta com ID {card_id}!")


@router.put("/{card_id}", response_model=CardRead, status_code=status.HTTP_200_OK)
def update_card(card_id: int, updated_card: CardUpdate, session: Session = Depends(get_session)):
    card = session.get(Card, card_id)

    if not card:
        raise HTTPException(404, f"Carta com ID {card_id} não existe!")

    card_dict = updated_card.model_dump(exclude_unset=True)
    if not card_dict:
        raise HTTPException(400, "Nenhum campo para atualizar")

    try:
        for key, value in card_dict.items():
            setattr(card, key, value)
        session.commit()
        session.refresh(card)
        return card

    except Exception as e:
        session.rollback()
        raise HTTPException(400, f"Não foi possível atualizar Carta com ID {card_id}!")


@router.get("/", response_model=list[CardRead], status_code=status.HTTP_200_OK)
def list_cards(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    try:
        cards = session.exec(
            select(Card).offset(skip).limit(limit)
        ).all()
        return cards

    except Exception as e:
        raise HTTPException(status_code=500, detail="Houve um erro interno no servidor")


@router.get("/search/{name}", response_model=list[CardRead], status_code=status.HTTP_200_OK)
def search_card_by_name(
    name: str,
    skip: int = 0,
    limit: int = Query(10, le=50),
    session: Session = Depends(get_session)
):
    try:
        cards = session.exec(
            select(Card)
            .where(Card.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        ).all()

        return cards

    except Exception as e:
        raise HTTPException(status_code=500, detail="Houve um erro interno no servidor")