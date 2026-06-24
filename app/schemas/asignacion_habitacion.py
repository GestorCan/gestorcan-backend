from pydantic import BaseModel
from datetime import date


class AsignacionHabitacionBase(BaseModel):
    estancia_id: int
    mascota_id: int
    habitacion_id: int
    fecha_entrada: date
    fecha_salida: date
    activa: bool = True


class AsignacionHabitacionCreate(AsignacionHabitacionBase):
    pass


class AsignacionHabitacionResponse(AsignacionHabitacionBase):
    id: int

    class Config:
        from_attributes = True

class ConfirmarAsignacionHabitacionRequest(BaseModel):
    estancia_id: int
    mascota_id: int
    habitacion_id: int
    fecha_entrada: date
    fecha_salida: date
    confirmar_compartida: bool = False