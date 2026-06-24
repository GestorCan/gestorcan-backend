from pydantic import BaseModel
from datetime import date


class AsignarHabitacionEstanciaRequest(BaseModel):

    mascota_id: int

    fecha_entrada: date

    fecha_salida: date

    confirmar_compartida: bool = False