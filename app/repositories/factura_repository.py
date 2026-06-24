# app/repositories/factura_repository.py

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.contador_factura import ContadorFactura
from app.models.factura import Factura




def generar_numero_factura(db: Session, serie: str = "2026"):

    anio = datetime.now().year

    contador = (
        db.query(ContadorFactura)
        .filter(
            ContadorFactura.serie == serie,
            ContadorFactura.anio == anio
        )
        .first()
    )

    # Si no existe contador para el año/serie
    if not contador:

        contador = ContadorFactura(
            serie=serie,
            anio=anio,
            ultimo_numero=1
        )

        db.add(contador)

    else:

        contador.ultimo_numero += 1

    db.commit()
    db.refresh(contador)

    numero = f"{serie}-{contador.ultimo_numero:06d}"

    return numero, serie


def listar_facturas(db):
    return (
        db.query(Factura)
        .order_by(Factura.fecha.desc(), Factura.id.desc())
        .all()
    )


def obtener_factura_por_id(db, factura_id: int):
    return (
        db.query(Factura)
        .filter(Factura.id == factura_id)
        .first()
    )