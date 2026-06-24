# app/models/habitacion.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text
)

from app.database import Base
from sqlalchemy import ForeignKey

class Habitacion(Base):
    __tablename__ = "habitaciones"

    id = Column(Integer, primary_key=True, index=True)

    residencia_id = Column(
        Integer,
        ForeignKey("residencias.id"),
        nullable=True
    )

    nombre = Column(String(100), nullable=False)

    grupo = Column(String(30), nullable=False)

    capacidad = Column(Integer, default=1)

    permite_camara = Column(Boolean, default=False)

    permite_compartir = Column(Boolean, default=False)

    estado = Column(String(30), default="libre")

    observaciones = Column(Text)

    activa = Column(Boolean, default=True)

