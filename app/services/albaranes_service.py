from app.repositories.albaranes_repository import obtener_albaranes

from app.database import SessionLocal
from sqlalchemy import text


from pathlib import Path
from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models.estancia import Estancia
from app.pdf.albaran_pdf import generar_pdf_albaran


MEDIA_ALBARANES = Path("media/albaranes")


def regenerar_pdf_albaran(estancia_id: int):
    db = SessionLocal()

    try:
        estancia = (
            db.query(Estancia)
            .options(
                joinedload(Estancia.cliente),
                joinedload(Estancia.mascota)
            )
            .filter(Estancia.id == estancia_id)
            .first()
        )

        if not estancia:
            return None

        MEDIA_ALBARANES.mkdir(parents=True, exist_ok=True)

        output_path = MEDIA_ALBARANES / f"albaran_{estancia.id}.pdf"

        generar_pdf_albaran(estancia, str(output_path))

        estancia.ruta_albaran_pdf = str(output_path)
        db.commit()

        return str(output_path)

    finally:
        db.close()
def obtener_ruta_pdf_albaran(estancia_id: int):
    db = SessionLocal()
    try:
        query = text("""
            SELECT ruta_albaran_pdf
            FROM estancias
            WHERE id = :id
        """)

        result = db.execute(query, {"id": estancia_id}).fetchone()

        if result:
            return result[0]

        return None

    finally:
        db.close()


from pathlib import Path
from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models.estancia import Estancia
from app.pdf.albaran_pdf import generar_pdf_albaran


MEDIA_ALBARANES = Path("media/albaranes")


def regenerar_pdf_albaran(estancia_id: int):
    db = SessionLocal()

    try:
        estancia = (
            db.query(Estancia)
            .options(
                joinedload(Estancia.cliente),
                joinedload(Estancia.mascota)
            )
            .filter(Estancia.id == estancia_id)
            .first()
        )

        if not estancia:
            return None

        MEDIA_ALBARANES.mkdir(parents=True, exist_ok=True)

        output_path = MEDIA_ALBARANES / f"albaran_{estancia.id}.pdf"

        generar_pdf_albaran(estancia, str(output_path))

        estancia.ruta_albaran_pdf = str(output_path)
        db.commit()

        return str(output_path)

    finally:
        db.close()
def listar_albaranes(cliente=None, fecha=None):
    albaranes = obtener_albaranes(cliente, fecha)

    for a in albaranes:
        if not a["ruta_albaran_pdf"]:
            # generar automáticamente
            pass

    return albaranes

