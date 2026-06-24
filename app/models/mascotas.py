from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Mascota(Base):
    __tablename__ = "mascotas"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"))

    nombre = Column(String)
    numero_chip = Column(String)
    raza = Column(String)
    edad = Column(String)
    tamano = Column(String)
    peso = Column(String)
    sexo = Column(String)
    vacunas = Column(String)
    enfermedades_medicacion = Column(String)
    comportamiento_personas = Column(String)
    comportamiento_perros = Column(String)
    foto = Column(String)
    observaciones = Column(String)

    cliente = relationship(
        "Cliente",
        back_populates="mascotas"
    )
