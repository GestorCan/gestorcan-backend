from pydantic import BaseModel, EmailStr
from typing import Optional


class ClienteBase(BaseModel):
    nombre: str
    apellidos: Optional[str] = None

    dni: Optional[str] = None

    tipo_documento: str = "NIF"

    telefono: Optional[str] = None
    email: Optional[EmailStr] = None

    redes_sociales: Optional[str] = None

    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    poblacion: Optional[str] = None
    provincia: Optional[str] = None

    observaciones: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    pass


class ClienteOut(ClienteBase):
    id: int

    class Config:
        from_attributes = True