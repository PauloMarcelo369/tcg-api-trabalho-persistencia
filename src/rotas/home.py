from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root():
    """Rota raiz da aplicação"""
    return {
        "message": "Bem-vindo à TCG API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/users",
            "decks": "/decks",
            "cards": "/cards",
            "collections": "/collections"
        }
    }


@router.get("/health")
def health_check():
    """Verifica se a API está funcionando"""
    return {"status": "ok"}
