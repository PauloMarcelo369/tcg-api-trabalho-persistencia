from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models.models import Collection

router = APIRouter(prefix="/collections", tags=["Collections"])


@router.post("/")
def create_collection(collection: Collection, session: Session = Depends(get_session)):
    """Cria uma nova coleção"""
    session.add(collection)
    session.commit()
    session.refresh(collection)
    return collection


@router.get("/")
def list_collections(session: Session = Depends(get_session)):
    """Lista todas as coleções"""
    collections = session.exec(select(Collection)).all()
    return collections


@router.get("/{collection_id}")
def get_collection(collection_id: int, session: Session = Depends(get_session)):
    """Obtém uma coleção por ID"""
    collection = session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    return collection


@router.put("/{collection_id}")
def update_collection(collection_id: int, collection_update: Collection, session: Session = Depends(get_session)):
    """Atualiza uma coleção"""
    collection = session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    
    collection_data = collection_update.dict(exclude_unset=True)
    for key, value in collection_data.items():
        setattr(collection, key, value)
    
    session.add(collection)
    session.commit()
    session.refresh(collection)
    return collection


@router.delete("/{collection_id}")
def delete_collection(collection_id: int, session: Session = Depends(get_session)):
    """Deleta uma coleção"""
    collection = session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")
    
    session.delete(collection)
    session.commit()
    return {"message": "Coleção deletada com sucesso"}
