# app/schemas/habitacion.py

from pydantic import BaseModel, field_validator
from typing import Optional

from app.constants.habitaciones import (
    GRUPOS_HABITACION,
    ESTADOS_HABITACION
)

from pydantic import BaseModel, field_validator



class HabitacionBase(BaseModel):

    residencia_id: int | None = None

    nombre: str

    grupo: str

    capacidad: int = 1

    permite_camara: bool = False

    permite_compartir: bool = False

    estado: str = "libre"

    observaciones: Optional[str] = None

    activa: bool = True


    # =====================================================
    # VALIDACIONES
    # =====================================================

    @field_validator("grupo")
    @classmethod
    def validar_grupo(cls, value):

        if value not in GRUPOS_HABITACION:
            raise ValueError("Grupo inválido")

        return value


    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):

        if value not in ESTADOS_HABITACION:
            raise ValueError("Estado inválido")

        return value


class HabitacionCreate(HabitacionBase):
    pass


class HabitacionUpdate(HabitacionBase):
    pass


class HabitacionResponse(HabitacionBase):

    id: int

    class Config:
        from_attributes = True


class HabitacionDashboardResponse(BaseModel):

    id: int
    nombre: str
    grupo: str
    capacidad: int
    estado: str

    permite_camara: bool
    permite_compartir: bool

    color: str
    icono: str

    texto_estado: str
    texto_capacidad: str

    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class GenerarHabitacionesRequest(BaseModel):
    grupo: str
    cantidad: int
    prefijo: str
    capacidad: int = 1
    permite_camara: bool = False
    permite_compartir: bool = False

    @field_validator("grupo")
    @classmethod
    def validar_grupo(cls, value):
        if value not in GRUPOS_HABITACION:
            raise ValueError("Grupo inválido")
        return value

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, value):
        if value < 1:
            raise ValueError("La cantidad debe ser mayor que 0")
        return value