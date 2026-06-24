from pydantic import BaseModel


class SugerirHabitacionRequest(BaseModel):

    residencia_id: int

    tamano_mascota: str