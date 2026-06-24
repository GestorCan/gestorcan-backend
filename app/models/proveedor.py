# app/models/proveedor.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func

from app.database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, unique=True, nullable=False)

    cif = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)

    tipo_gasto_defecto = Column(String, nullable=True)

    tiene_retencion = Column(Boolean, default=False)
    porcentaje_retencion_defecto = Column(Float, default=0)



    created_at = Column(DateTime, server_default=func.now())