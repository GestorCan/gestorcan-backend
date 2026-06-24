from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Numeric,
    Boolean,
    ForeignKey,Text
)

from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship


estancia = relationship("Estancia", back_populates="factura")

class Factura(Base):

    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)

    numero_factura = Column(String, nullable=False, unique=True)
    serie = Column(String, nullable=False)

    fecha = Column(Date, nullable=False)

    cliente = relationship("Cliente")
    estancia = relationship("Estancia")
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    estancia_id = Column(
        Integer,
        ForeignKey("estancias.id"),
        nullable=True
    )

    base_imponible = Column(Numeric(10, 2), nullable=False)
    iva = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)

    estado_pago = Column(String, default="pendiente")

    pdf_path = Column(String, nullable=True)
    qr_path = Column(String, nullable=True)

    hash_anterior = Column(String)
    hash_actual = Column(String)

    fecha_hora_huso_gen_registro = Column(
        String,
        nullable=True
    )

    verifactu_enviado = Column(Boolean, default=False)
    fecha_envio_verifactu = Column(DateTime, nullable=True)

    # =========================
    # FACTURAS RECTIFICATIVAS
    # =========================

    tipo_factura = Column(
        String(20),
        default="ordinaria"
    )

    factura_rectificada_id = Column(
        Integer,
        ForeignKey("facturas.id"),
        nullable=True
    )

    motivo_rectificacion = Column(
        Text,
        nullable=True
    )

    tipo_rectificativa = Column(
        String(5),
        nullable=True
    )

    serie_rectificativa = Column(
        String(20),
        nullable=True
    )

    created_at = Column(DateTime, server_default=func.now())

    #estancia = relationship("Estancia",back_populates="factura" )
