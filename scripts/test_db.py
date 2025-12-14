#VERIFICA CONEXÃO COM O BANCO DE DADOS
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        r = conn.execute(text("SELECT 1"))
        print("DB OK:", r.scalar())
except Exception as e:
    print("DB CONNECTION ERROR:", e)
