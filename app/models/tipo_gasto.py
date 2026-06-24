# app/models/tipo_gasto.py

from sqlalchemy import Column, Integer, String,Float
from app.database import Base


class TipoGasto(Base):
    __tablename__ = "tipos_gasto"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, unique=True, nullable=False)

    iva_defecto = Column(Float, default=21)