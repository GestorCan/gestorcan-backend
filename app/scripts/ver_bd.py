from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

from app.database import engine, SessionLocal

print("ENGINE URL:", engine.url)

db = SessionLocal()

try:
    tablas = db.execute(text("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)).fetchall()

    print("\nTABLAS ENCONTRADAS:")
    for t in tablas:
        print("-", t[0])

    print("\nCOLUMNAS ESTANCIAS:")
    cols = db.execute(text("PRAGMA table_info(estancias)")).fetchall()
    for col in cols:
        print(col)

    print("\nCOLUMNAS MASCOTAS:")
    cols = db.execute(text("PRAGMA table_info(mascotas)")).fetchall()
    for col in cols:
        print(col)

    print("\nCOLUMNAS CLIENTES:")
    cols = db.execute(text("PRAGMA table_info(clientes)")).fetchall()
    for col in cols:
        print(col)

finally:
    db.close()