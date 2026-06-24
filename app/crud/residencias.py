from sqlalchemy.orm import Session
from app.models.residencias import Residencia


def obtener_residencia(db: Session, residencia_id: int):

    return db.query(Residencia)\
        .filter(Residencia.id == residencia_id)\
        .first()


def actualizar_residencia(
    db: Session,
    residencia_id: int,
    datos
):

    residencia = db.query(Residencia)\
        .filter(Residencia.id == residencia_id)\
        .first()

    if not residencia:
        return None

    for campo, valor in datos.dict().items():
        setattr(residencia, campo, valor)

    db.commit()
    db.refresh(residencia)

    return residencia