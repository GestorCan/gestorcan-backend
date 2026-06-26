from app.database import SessionLocal
from app.models.tarifa_model import Tarifa
from sqlalchemy import func



def obtener_precio_tarifa(concepto: str, tipo: str):
    db = SessionLocal()

    try:
        tarifa = (
            db.query(Tarifa)
            .filter(
                func.lower(Tarifa.concepto) == concepto.lower(),
                func.lower(Tarifa.tipo) == tipo.lower(),
                Tarifa.activo == True
            )
            .first()
        )

        return tarifa.precio if tarifa else 0

    finally:
        db.close()