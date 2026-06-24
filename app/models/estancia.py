# app/models/estancia.py

from sqlalchemy import Column, Integer, String, Date, Time, Numeric, Boolean, ForeignKey, Text,Float
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.orm import relationship

class Estancia(Base):
    __tablename__ = "estancias"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    mascota_id = Column(Integer, ForeignKey("mascotas.id"), nullable=False)

    fecha_entrada = Column(Date, nullable=False)
    hora_entrada = Column(Time, nullable=True)

    fecha_salida = Column(Date, nullable=False)
    hora_salida = Column(Time, nullable=True)

    habitacion = Column(String(50), nullable=True)

    tipo_precio_dia = Column(String(50), nullable=False, default="normal")

    precio_dia = Column(Numeric(10, 2), nullable=False, default=0)
    num_dias = Column(Integer, nullable=False, default=1)

    extras = Column(Text, nullable=True)
    importe_extras = Column(Numeric(10, 2), nullable=False, default=0)

    camaras = Column(Boolean, default=False)
    importe_camaras = Column(Numeric(10, 2), nullable=False, default=0)

    transporte = Column(Boolean, default=False)
    importe_transporte = Column(Numeric(10, 2), nullable=False, default=0)

    kilometros = Column(Float, default=0)


    veterinario = Column(Boolean, default=False)
    importe_veterinario = Column(Numeric(10, 2), nullable=False, default=0)

    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    total = Column(Numeric(10, 2), nullable=False, default=0)

    pagado = Column(Boolean, default=False)
    facturado = Column(Boolean, default=False)

    observaciones = Column(Text, nullable=True)

    cliente = relationship("Cliente")
    mascota = relationship("Mascota")

    pienso = Column(Boolean, default=False)
    importe_pienso = Column(Numeric(10, 2), nullable=False, default=0)


    #factura = relationship("Factura", back_populates="estancia", uselist=False)


