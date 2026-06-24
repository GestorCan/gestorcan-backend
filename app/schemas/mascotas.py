from pydantic import BaseModel
from typing import Optional


class MascotaBase(BaseModel):
    cliente_id: int

    nombre: str
    numero_chip: Optional[str] = None
    raza: Optional[str] = None
    edad: Optional[int] = None

    tamano: Optional[str] = None
    peso: Optional[str] = None

    sexo: Optional[str] = None
    vacunas: Optional[str] = None

    enfermedades_medicacion: Optional[str] = None

    comportamiento_personas: Optional[str] = None
    comportamiento_perros: Optional[str] = None


class MascotaCreate(MascotaBase):
    pass


class MascotaOut(MascotaBase):
    id: int

    class Config:
        from_attributes = True

class MascotaUpdate(MascotaBase):
    pass