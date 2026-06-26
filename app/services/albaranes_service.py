from pathlib import Path

from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models.estancia import Estancia
from app.pdf.albaran_pdf import generar_pdf_albaran
from app.repositories.albaranes_repository import obtener_albaranes


MEDIA_ALBARANES = Path("media/albaranes")


def regenerar_pdf_albaran(estancia_id: int):
    db = SessionLocal()

    try:
        estancia = (
            db.query(Estancia)
            .options(
                joinedload(Estancia.cliente),
                joinedload(Estancia.mascota),
            )
            .filter(Estancia.id == estancia_id)
            .first()
        )

        if not estancia:
            return None

        MEDIA_ALBARANES.mkdir(parents=True, exist_ok=True)

        output_path = MEDIA_ALBARANES / f"albaran_{estancia.id}.pdf"

        generar_pdf_albaran(estancia, str(output_path))

        return str(output_path)

    finally:
        db.close()


def obtener_ruta_pdf_albaran(estancia_id: int):
    output_path = MEDIA_ALBARANES / f"albaran_{estancia_id}.pdf"

    if output_path.exists():
        return str(output_path)

    return regenerar_pdf_albaran(estancia_id)


def listar_albaranes(cliente=None, fecha=None):
    albaranes = obtener_albaranes(cliente, fecha)

    for a in albaranes:
        estancia_id = a.get("id") or a.get("estancia_id")

        if estancia_id:
            ruta = obtener_ruta_pdf_albaran(estancia_id)
            a["ruta_albaran_pdf"] = ruta

    return albaranes