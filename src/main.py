from fastapi import FastAPI
from rotas import home, users, decks, cards, collections

# Inicializa o aplicativo FastAPI
app = FastAPI(
    title="TCG API",
    description="API para gerenciar cartas e decks de jogo de cartas",
    version="1.0.0"
)

# Rotas para Endpoints
app.include_router(home.router)
app.include_router(users.router)
app.include_router(decks.router)
app.include_router(cards.router)
app.include_router(collections.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)