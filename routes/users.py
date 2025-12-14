from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from database import get_session
from models.models import User
from models.models import Deck
from routes.schemas.userSchema import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

from pydantic import ValidationError

#cria novo usuario
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == data.email)).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado!")

    try:
        user = User.model_validate(data)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao criar usuário!")

#retorna usuario pelo id
@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if (not user):
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")
    return user


#lista todos os usuarios
@router.get("/", response_model=List[UserRead], status_code=status.HTTP_200_OK)
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@router.get("/{user_id}/decks/count", response_model=int, status_code=status.HTTP_200_OK)
def count_user_decks(user_id: int, session: Session = Depends(get_session)):
    """Return the number of decks for a user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")

    decks = session.exec(select(Deck).where(Deck.user_id == user_id)).all()
    return len(decks)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(user_id: int, session: Session = Depends(get_session)):
    """Delete a User"""
    user = session.get(User, user_id)
    if (not user):
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")

    try:
        session.delete(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(400, f"Houve um problema ao deletar o Usuário com ID {user_id}!")


@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
def put(user_id: int, updated_user: UserUpdate,  session: Session = Depends(get_session)):
    user = session.get(User, user_id)

    if (not user):
        raise HTTPException(404, f"Usuário com ID {user_id} não existe!")

    user_dict = updated_user.model_dump(exclude_unset=True)
    if not user_dict:
        raise HTTPException(400, "Nenhum campo para atualizar")
    
    try:
        for key, value in user_dict.items():
            setattr(user, key, value)
        session.commit()
        session.refresh(user)
        return user
    
    except Exception as e:
        session.rollback()
        raise HTTPException(400, f"Não foi possível atualizar Usuário com ID {user_id}!")
