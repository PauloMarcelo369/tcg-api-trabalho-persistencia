from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlmodel import Session, select
from database import get_session
from models.models import Collection
from routes.schemas.collectionSchema import CollectionCreate, CollectionRead, CollectionUpdate
from pydantic import ValidationError


router = APIRouter(prefix="/collections", tags=["Collections"])


@router.post("/", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
def create_collection(data: CollectionCreate, session: Session = Depends(get_session)):
    """Create a new collection"""
    existing = session.exec(select(Collection).where(Collection.name == data.name)).first()

    if existing:
        raise HTTPException(status_code=400, detail="Collection com esse nome já existe!")

    try:
        collection = Collection.model_validate(data)
        session.add(collection)
        session.commit()
        session.refresh(collection)
        return collection

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao criar collection!")


@router.get("/{collection_id}", response_model=CollectionRead, status_code=status.HTTP_200_OK)
def get_collection_by_id(collection_id: int, session: Session = Depends(get_session)):
    """Get Collection by ID"""
    collection = session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(404, f"Collection com ID {collection_id} não existe!")
    return collection


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection_by_id(collection_id: int, session: Session = Depends(get_session)):
    """Delete a Collection"""
    collection = session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(404, f"Collection com ID {collection_id} não existe!")

    try:
        session.delete(collection)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(400, f"Houve um problema ao deletar a Collection com ID {collection_id}!")


@router.put("/{collection_id}", response_model=CollectionRead, status_code=status.HTTP_200_OK)
def update_collection(collection_id: int, updated_collection: CollectionUpdate, session: Session = Depends(get_session)):
    collection = session.get(Collection, collection_id)

    if not collection:
        raise HTTPException(404, f"Collection com ID {collection_id} não existe!")

    collection_dict = updated_collection.model_dump(exclude_unset=True)
    if not collection_dict:
        raise HTTPException(400, "Nenhum campo para atualizar")

    try:
        for key, value in collection_dict.items():
            setattr(collection, key, value)
        session.commit()
        session.refresh(collection)
        return collection

    except Exception as e:
        session.rollback()
        raise HTTPException(400, f"Não foi possível atualizar Collection com ID {collection_id}!")


@router.get("/", response_model=list[CollectionRead], status_code=status.HTTP_200_OK)
def list_collections(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    try:
        collections = session.exec(
            select(Collection)
            .order_by(Collection.release_date.desc())
            .offset(skip)
            .limit(limit)
        ).all()
        return collections

    except Exception as e:
        raise HTTPException(status_code=500, detail="Houve um erro interno no servidor")


@router.get("/search/{name}", response_model=list[CollectionRead], status_code=status.HTTP_200_OK)
def search_collection_by_name(
    name: str,
    skip: int = 0,
    limit: int = Query(10, le=50),
    session: Session = Depends(get_session)
):
    try:
        collections = session.exec(
            select(Collection)
            .where(Collection.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        ).all()

        return collections

    except Exception as e:
        raise HTTPException(status_code=500, detail="Houve um erro interno no servidor")