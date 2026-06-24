from sqlalchemy import Column, Integer, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class AsignacionHabitacion(Base):
    __tablename__ = "asignaciones_habitacion"

    id = Column(Integer, primary_key=True, index=True)

    estancia_id = Column(Integer, ForeignKey("estancias.id"), nullable=False)
    mascota_id = Column(Integer, ForeignKey("mascotas.id"), nullable=False)
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id"), nullable=False)

    fecha_entrada = Column(Date, nullable=False)
    fecha_salida = Column(Date, nullable=False)

    activa = Column(Boolean, default=True)