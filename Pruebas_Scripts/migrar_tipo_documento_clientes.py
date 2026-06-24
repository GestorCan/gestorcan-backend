import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///C:/Users/cualq/gestorcan-backend/gestorcan_local.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
from app.models.clientes import Cliente
from app.models.mascotas import Mascota


def limpiar_documento(valor: str) -> str:
    if not valor:
        return ""

    return (
        valor.strip()
        .upper()
        .replace("-", "")
        .replace(" ", "")
    )


def detectar_tipo_documento(valor: str) -> str:
    doc = limpiar_documento(valor)

    if re.fullmatch(r"\d{8}[A-Z]", doc):
        return "NIF"

    if re.fullmatch(r"[XYZ]\d{7}[A-Z]", doc):
        return "NIE"

    if re.fullmatch(r"[ABCDEFGHJKLMNPQRSUVW]\d{7}[0-9A-J]", doc):
        return "CIF"

    if re.fullmatch(r"[A-Z]{2}\d{6,9}", doc):
        return "PASAPORTE"

    return "OTRO"


def migrar():
    db = SessionLocal()

    try:
        clientes = db.query(Cliente).all()

        actualizados = 0

        for cliente in clientes:
            if not cliente.dni:
                continue

            nuevo_tipo = detectar_tipo_documento(cliente.dni)

            # No tocamos cliente.dni para evitar conflictos UNIQUE
            cliente.tipo_documento = nuevo_tipo

            actualizados += 1

        db.commit()

        print(f"Clientes revisados/actualizados: {actualizados}")

    except Exception as e:
        db.rollback()
        print("Error en migración:", e)

    finally:
        db.close()


if __name__ == "__main__":
    migrar()