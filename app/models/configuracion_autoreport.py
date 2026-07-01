# app/models/configuracion_autoreport.py

from sqlalchemy import Column, Integer, Boolean, String

from app.database import Base


class ConfiguracionAutoreport(Base):
    __tablename__ = "configuracion_autoreport"

    id = Column(Integer, primary_key=True)

    activo = Column(Boolean, default=True)

    hora_envio = Column(String, default="21:00")

    destinatarios = Column(String)

    dias_adelante = Column(Integer, default=1)

    dias_ocupacion = Column(Integer, default=7)