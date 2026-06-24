# app/models/gasto.py

from sqlalchemy import Column, Integer, String, Float, Date, DateTime,Boolean
from sqlalchemy.sql import func

from app.database import Base


class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, index=True)

    tipo_documento = Column(String, nullable=False)  # ticket / factura

    fecha = Column(Date, nullable=False)

    proveedor_id = Column(Integer, nullable=True)
    proveedor = Column(String, nullable=False)

    tipo_gasto = Column(String, nullable=False)

    # Ticket
    importe = Column(Float, default=0)

    # Factura
    numero_factura = Column(String, nullable=True)
    concepto = Column(String, nullable=True)

    base_imponible = Column(Float, default=0)
    porcentaje_iva = Column(Float, default=0)
    importe_iva = Column(Float, default=0)

    porcentaje_retencion = Column(Float, default=0)
    importe_retencion = Column(Float, default=0)

    total_factura = Column(Float, default=0)

    incluida_paquete_asesor = Column(Boolean, default=False)
    ejercicio_paquete_asesor = Column(Integer, nullable=True)
    trimestre_paquete_asesor = Column(Integer, nullable=True)
    fecha_inclusion_paquete = Column(DateTime, nullable=True)

    # Archivo
    archivo_path = Column(String, nullable=True)

    created_at = Column( DateTime, server_default=func.now() )

