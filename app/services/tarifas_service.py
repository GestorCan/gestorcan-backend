from app.database import SessionLocal
from app.models.tarifa_model import Tarifa


def obtener_precio_tarifa(concepto: str, tipo: str):
    db = SessionLocal()

    try:
        tarifa = (
            db.query(Tarifa)
            .filter(
                Tarifa.concepto == concepto,
                Tarifa.tipo == tipo,
                Tarifa.activo == True
            )
            .first()
        )

        return tarifa.precio if tarifa else 0

    finally:
        db.close()