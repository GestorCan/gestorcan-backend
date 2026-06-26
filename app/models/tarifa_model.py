# app/models/tarifa_model.py

from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

class Tarifa(Base):
    __tablename__ = "tarifas"

    id = Column(Integer, primary_key=True, index=True)

    concepto = Column(String, nullable=False)  # estancia_dia / servicio / extra
    tipo = Column(String, nullable=False)      # normal / camaras / lavado...
    precio = Column(Float, nullable=False, default=0)

    unidad = Column(String, default="unidad")  # dia / km / unidad

    activo = Column(Boolean, default=True)