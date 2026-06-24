# app/schemas/estancia.py

from pydantic import BaseModel
from datetime import date, time
from decimal import Decimal
from typing import Optional


class EstanciaBase(BaseModel):
    cliente_id: int
    mascota_id: int

    fecha_entrada: date
    hora_entrada: Optional[time] = None

    fecha_salida: date
    hora_salida: Optional[time] = None

    habitacion: Optional[str] = None

    tipo_precio_dia: str = "normal"

    precio_dia: Decimal = Decimal("0.00")
    num_dias: int = 1

    extras: Optional[str] = None
    importe_extras: Decimal = Decimal("0.00")

    camaras: bool = False
    importe_camaras: Decimal = Decimal("0.00")

    transporte: bool = False
    kilometros: Decimal = Decimal("0.00")
    precio_km: Decimal = Decimal("0.00")
    importe_transporte: Decimal = Decimal("0.00")

    veterinario: bool = False
    importe_veterinario: Decimal = Decimal("0.00")

    subtotal: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")

    pagado: bool = False
    observaciones: Optional[str] = None

    pienso: bool = False
    importe_pienso: Decimal = Decimal("0.00")



class EstanciaCreate(EstanciaBase):
    pass


class EstanciaUpdate(EstanciaBase):
    pass


class EstanciaOut(EstanciaBase):
    id: int
    num_dias: int
    subtotal: Decimal
    total: Decimal
    facturado: bool

    class Config:
        from_attributes = True