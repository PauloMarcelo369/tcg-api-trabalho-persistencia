from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlmodel import Session, select, func
from database import get_session
from sqlalchemy.orm import selectinload
from models.models import Deck, DeckCardLink, Card, DeckFormat
from routes.schemas.deckShema import DeckCreate, DeckRead, DeckUpdate, DeckWithCardsRead, DeckCardsLinkRead
from pydantic import ValidationError


router = APIRouter(
    prefix="/decks", 
    tags=["Decks"]
)



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
    

@router.post("/{deck_id}/cards/{card_id}", response_model=DeckCardsLinkRead, status_code=status.HTTP_201_CREATED)
def add_card_in_deck(
    deck_id: int,
    card_id: int,
    session: Session = Depends(get_session),
):
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(404, f"Deck com ID {deck_id} não existe!")

    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(404, f"Card com ID {card_id} não existe!")

    card_in_deck = session.exec(
        select(DeckCardLink)
        .where(
            DeckCardLink.deck_id == deck_id,
            DeckCardLink.card_id == card_id,
        )
    ).first()

    try:
        if card_in_deck:
            if card_in_deck.qty == 3:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Esta carta já atingiu o limite máximo permitido no deck"
                )

            card_in_deck.qty += 1
        else:
            card_in_deck = DeckCardLink(
                deck_id=deck_id,
                card_id=card_id,
                qty=1
            )
            session.add(card_in_deck)

        session.commit()
        session.refresh(card_in_deck)

        return {
            "deck_id": deck_id,
            "card_id": card_id,
            "qty": card_in_deck.qty
        }

    except HTTPException:
        raise
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao tentar adicionar card ao deck"
        )

@router.delete("/{deck_id}/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card_in_deck(
    deck_id: int,
    card_id: int,
    session: Session = Depends(get_session),
):
    deck = session.get(Deck, deck_id)
    if not deck:
        raise HTTPException(404, f"Deck com ID {deck_id} não existe!")

    card = session.get(Card, card_id)
    if not card:
        raise HTTPException(404, f"Card com ID {card_id} não existe!")

    card_in_deck = session.exec(
        select(DeckCardLink)
        .where(
            DeckCardLink.deck_id == deck_id,
            DeckCardLink.card_id == card_id,
        )
    ).first()

    try:
        if not card_in_deck:
           raise HTTPException(404, "card não existe no deck")
        
        if card_in_deck.qty > 1:
            card_in_deck.qty = card_in_deck.qty - 1
            session.add(card_in_deck)
        else:
            session.delete(card_in_deck)

        session.commit()

    except HTTPException:
        raise
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao tentar remover card ao deck"
        )


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
    



@router.get("/", response_model=list[DeckRead], status_code=status.HTTP_200_OK)
def list_decks( 
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    try:
        decks = session.exec(
            select(Deck).offset(skip).limit(limit)
        ).all()
        return decks
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Houve um erro interno no servidor")



@router.get("/stats/decks-by-format", status_code=status.HTTP_200_OK)
def decks_by_format(
    session: Session = Depends(get_session)
):
    try:
        rows = session.exec(
            select(
                Deck.format,
                func.count(Deck.id).label("total_decks")
            )
            .group_by(Deck.format)
        ).all()

        return [
            {
                "format": row[0],
                "total_decks": row[1],
            }
            for row in rows
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Houve um erro interno no servidor")
    



@router.get("/average-cards-per-deck", status_code=status.HTTP_200_OK)
def average_cards_per_deck(session: Session = Depends(get_session)):
    try:
        subq = (
            select(
                Deck.id,
                func.sum(DeckCardLink.qty).label("total_cards")
            )
            .join(DeckCardLink)
            .group_by(Deck.id)
            .subquery()
        )
        avg = session.exec(select(func.avg(subq.c.total_cards))).one()
        return {
            "average_cards_per_deck": avg
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Houve um erro interno no servidor")
    



@router.get("/{deck_id}", response_model=DeckRead,status_code=status.HTTP_200_OK)
def get_deck_by_id(deck_id : int, session: Session = Depends(get_session)):
    """Get Deck by ID"""
    deck = session.get(Deck, deck_id)
    if (not deck):
        raise HTTPException(404, f"Deck com ID {deck_id} não existe!")
    return deck


@router.get("/search/{name}",response_model=list[DeckRead], status_code=status.HTTP_200_OK)
def search_deck_by_name(
    name : str,
    skip: int = 0,
    limit: int = Query(10, le=50),
    session: Session = Depends(get_session)
):
    try:
        decks = session.exec(
            select(Deck)
            .where(Deck.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        ).all()

        return decks
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Houve um erro interno no servidor")


@router.get("/{deck_id}/with-cards", response_model=DeckWithCardsRead, status_code=status.HTTP_200_OK)
def get_deck_with_cards(deck_id : int, session: Session = Depends(get_session)):
    deck = session.exec(
        select(Deck)
        .where(Deck.id == deck_id)
        .options(selectinload(Deck.cards))
    ).first()

    if (not deck):
        raise HTTPException(404, "Deck não encontrado")

    return deck

@router.get("/{deck_id}/cards/count", status_code=status.HTTP_200_OK)
def count_cards_in_deck(deck_id : int,session : Session = Depends(get_session)):
    try:
        count = session.exec(
            select(func.sum(DeckCardLink.qty))
            .where(DeckCardLink.deck_id == deck_id)
        ).one()

        return {"deck_id" : deck_id, "total_cards" : count or 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Houve um erro interno no servidor")