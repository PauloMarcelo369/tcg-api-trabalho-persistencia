from fastapi import FastAPI
from routes import decks, users, cards

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Tcg API is running"}

app.include_router(decks.router)
app.include_router(users.router)
app.include_router(cards.router)
