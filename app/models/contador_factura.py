# app/models/contador_factura.py

from sqlalchemy import Column, Integer, String, UniqueConstraint
from app.database import Base


class ContadorFactura(Base):
    __tablename__ = "contadores_factura"

    id = Column(Integer, primary_key=True, index=True)

    serie = Column(String, nullable=False)
    anio = Column(Integer, nullable=False)
    ultimo_numero = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("serie", "anio", name="uq_serie_anio_factura"),
    )