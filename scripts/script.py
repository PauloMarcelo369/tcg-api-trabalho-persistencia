from sqlmodel import Session
from datetime import datetime, date
from database import engine

from models.models import (
    User, Deck, Card, Collection,
    CardType, CardRarity, DeckFormat, DeckCardLink
)

def seed():
    with Session(engine) as session:

        # -----------------------------------------------------------
        # USERS – nomes reais
        # -----------------------------------------------------------
        users = [
            User(name="Lucas Almeida", email="lucas.almeida@example.com", password="123"),
            User(name="Mariana Torres", email="mariana.torres@example.com", password="123"),
            User(name="Pedro Santos", email="pedro.santos@example.com", password="123"),
            User(name="Julia Ramos", email="julia.ramos@example.com", password="123"),
            User(name="Thiago Martins", email="thiago.martins@example.com", password="123"),
            User(name="Ana Garcia", email="ana.garcia@example.com", password="123"),
            User(name="Rafael Lima", email="rafael.lima@example.com", password="123"),
            User(name="Carolina Mota", email="carolina.mota@example.com", password="123"),
            User(name="Gustavo Freitas", email="gustavo.freitas@example.com", password="123"),
            User(name="Beatriz Rocha", email="beatriz.rocha@example.com", password="123"),
        ]
        for u in users:
            session.add(u)

        # -----------------------------------------------------------
        # COLLECTIONS – nomes plausíveis
        # -----------------------------------------------------------
        collections = [
            Collection(name="Alpha Set", release_date=date(2020, 3, 21)),
            Collection(name="Mystic Legends", release_date=date(2021, 8, 12)),
            Collection(name="Dragon’s Rebirth", release_date=date(2022, 5, 3)),
            Collection(name="Warrior’s Path", release_date=date(2021, 2, 10)),
            Collection(name="Arcane Secrets", release_date=date(2023, 1, 15)),
            Collection(name="Dino Age", release_date=date(2020, 11, 8)),
            Collection(name="Spellbound Realm", release_date=date(2024, 4, 27)),
            Collection(name="Ancient North", release_date=date(2022, 7, 19)),
            Collection(name="Forgotten Dawn", release_date=date(2023, 9, 9)),
            Collection(name="Prime Edition", release_date=date(2024, 2, 4)),
        ]
        for c in collections:
            session.add(c)

        session.commit()

        # -----------------------------------------------------------
        # CARDS – coerentes com o tipo da coleção
        # -----------------------------------------------------------
        cards_data = [
            # Alpha Set
            ("Blazing Young Dragon", CardType.Dragon, CardRarity.Common, 1),
            ("Forest Warrior", CardType.Warrior, CardRarity.Uncommon, 1),

            # Mystic Legends
            ("Arcane Apprentice", CardType.Magician, CardRarity.Common, 2),
            ("Mystic Dragon Elder", CardType.Dragon, CardRarity.Rare, 2),

            # Dragon’s Rebirth
            ("Reborn Flame Dragon", CardType.Dragon, CardRarity.Mythic, 3),
            ("Dragon Shrine Keeper", CardType.Mage, CardRarity.Uncommon, 3),

            # Warrior’s Path
            ("Steelblade Knight", CardType.Warrior, CardRarity.Rare, 4),
            ("Twin Axe Veteran", CardType.Warrior, CardRarity.Common, 4),

            # Arcane Secrets
            ("Grand Magus Aeron", CardType.Magician, CardRarity.Mythic, 5),
            ("Forbidden Spellbook", CardType.Spell, CardRarity.Rare, 5),

            # Dino Age
            ("Alpha Tyrannus", CardType.Dinosaur, CardRarity.Rare, 6),
            ("Swift Raptor", CardType.Dinosaur, CardRarity.Common, 6),

            # Spellbound Realm
            ("Eternal Binding", CardType.Spell, CardRarity.Rare, 7),
            ("Arcane Shieldburst", CardType.Spell, CardRarity.Common, 7),

            # Ancient North
            ("Frostborn Dragon", CardType.Dragon, CardRarity.Mythic, 8),
            ("Northern Battle-Mage", CardType.Mage, CardRarity.Uncommon, 8),

            # Forgotten Dawn
            ("Forgotten Guardian", CardType.Warrior, CardRarity.Rare, 9),

            # Prime Edition
            ("Primeval Oracle", CardType.Mage, CardRarity.Rare, 10),
        ]

        cards = []
        for name, type_, rarity, collection_idx in cards_data:
            card = Card(
                name=name,
                type=type_,
                rarity=rarity,
                text=f"Card effect for {name}.",
                collection_id=collections[collection_idx - 1].id
            )
            cards.append(card)
            session.add(card)

        session.commit()

        # -----------------------------------------------------------
        # DECKS – nomes que fazem sentido
        # -----------------------------------------------------------
        deck_data = [
            ("Dragon Fury", DeckFormat.Standard),
            ("Mage’s Awakening", DeckFormat.Modern),
            ("Warrior Battalion", DeckFormat.Pauper),
            ("Ancient Roar", DeckFormat.Commander),
            ("Arcane Control", DeckFormat.Modern),
            ("Dino Breakers", DeckFormat.Standard),
            ("Frost Dominion", DeckFormat.Commander),
            ("Spell Overload", DeckFormat.Modern),
            ("Forgotten Vanguard", DeckFormat.Standard),
            ("Prime Arcana", DeckFormat.Commander),
        ]

        decks = []
        for i, (name, fmt) in enumerate(deck_data):
            deck = Deck(
                name=name,
                format=fmt,
                user_id=users[i].id
            )
            decks.append(deck)
            session.add(deck)

        session.commit()

        # -----------------------------------------------------------
        # ADD CARDS TO DECKS – coerente com o tema
        # -----------------------------------------------------------

        deck_themes = {
            "Dragon Fury": ["Dragon"],
            "Mage’s Awakening": ["Magician", "Mage"],
            "Warrior Battalion": ["Warrior"],
            "Ancient Roar": ["Dinosaur"],
            "Arcane Control": ["Spell", "Mage"],
            "Dino Breakers": ["Dinosaur"],
            "Frost Dominion": ["Dragon", "Mage"],
            "Spell Overload": ["Spell"],
            "Forgotten Vanguard": ["Warrior"],
            "Prime Arcana": ["Mage"],
        }

        for deck in decks:
            allowed_types = deck_themes[deck.name]
            deck_cards = [c for c in cards if c.type.value in allowed_types]

            # pega até 4 cartas do tema
            for card in deck_cards[:4]:
                session.add(DeckCardLink(
                    deck_id=deck.id,
                    card_id=card.id,
                    qty=1
                ))

        session.commit()

        print("✔ Banco populado com dados realistas!")

if __name__ == "__main__":
    seed()
