# app/models/cliente.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String)
    apellidos = Column(String)
    documento = Column(String)  # ya existente
    dni = Column(String)
    tipo_documento = Column(
        String(20),
        nullable=False,
        default="NIF",
        server_default="NIF"
    )


    telefono = Column(String)
    email = Column(String)
    direccion = Column(String)
    codigo_postal = Column(String)
    poblacion = Column(String)
    provincia = Column(String)
    redes_sociales = Column(String)
    observaciones = Column(String)

    mascotas = relationship(
        "Mascota",
        back_populates="cliente"
    )