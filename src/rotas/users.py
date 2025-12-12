from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models.models import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/")
def create_user(user: User, session: Session = Depends(get_session)):
    """Cria um novo usuário"""
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/")
def list_users(session: Session = Depends(get_session)):
    """Lista todos os usuários"""
    users = session.exec(select(User)).all()
    return users


@router.get("/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Obtém um usuário por ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.put("/{user_id}")
def update_user(user_id: int, user_update: User, session: Session = Depends(get_session)):
    """Atualiza um usuário"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    """Deleta um usuário"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    session.delete(user)
    session.commit()
    return {"message": "Usuário deletado com sucesso"}
