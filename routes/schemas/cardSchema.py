from sqlmodel import SQLModel

class CardRead(SQLModel):
    id: int
    name: str
