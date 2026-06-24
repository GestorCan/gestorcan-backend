from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Text
)

from sqlalchemy.sql import func

from app.database import Base


class VeriFactuRegistro(Base):
    __tablename__ = "verifactu_registros"

    id = Column(Integer, primary_key=True)

    factura_id = Column(Integer, ForeignKey("facturas.id"))

    numero_factura = Column(String)
    tipo_factura = Column(String)

    tipo_registro = Column(String)
    estado = Column(String)

    hash_anterior = Column(String)
    hash_actual = Column(String)

    qr_path = Column(String)
    xml_path = Column(String)

    enviado = Column(Boolean)

    fecha_envio = Column(DateTime, nullable=True)

    respuesta_aeat = Column(Text, nullable=True)

    csv_aeat = Column(String, nullable=True)

    estado_aeat = Column(String, nullable=True)

    codigo_error_aeat = Column(String, nullable=True)

    descripcion_error_aeat = Column(Text, nullable=True)

    timestamp_presentacion = Column(DateTime, nullable=True)

    signed_xml_path = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )