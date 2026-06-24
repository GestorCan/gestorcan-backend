# app/schemas/residencia.py

from pydantic import BaseModel
from typing import Optional


class ResidenciaBase(BaseModel):
    nombre: str
    razon_social: Optional[str] = None
    cif: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    pais: Optional[str] = None

    telefono: Optional[str] = None
    email: Optional[str] = None
    web: Optional[str] = None

    logo_url: Optional[str] = None
    color_principal: Optional[str] = "#3CB371"
    color_secundario: Optional[str] = "#1E293B"

    iva_defecto: float = 21.0
    iban: Optional[str] = None
    swift: Optional[str] = None
    serie_facturacion: Optional[str] = "A"

    hora_checkin: Optional[str] = "12:00"
    hora_checkout: Optional[str] = "10:00"

    permite_compartidas: bool = True
    permite_camaras: bool = True

    activa: bool = True


class ResidenciaCreate(ResidenciaBase):
    pass


class ResidenciaUpdate(ResidenciaBase):
    pass


class ResidenciaResponse(ResidenciaBase):
    id: int

    class Config:
        from_attributes = True