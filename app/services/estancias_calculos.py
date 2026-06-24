# app/services/estancias_calculos.py

from datetime import date
from decimal import Decimal
from datetime import time

def calcular_num_dias(fecha_entrada, fecha_salida, hora_salida=None):
    dias = (fecha_salida - fecha_entrada).days

    if hora_salida:
        if isinstance(hora_salida, str):
            partes = hora_salida.split(":")
            hora_salida = time(
                int(partes[0]),
                int(partes[1])
            )

        if hora_salida > time(12, 0):
            dias += 1

    return max(dias, 1)


from decimal import Decimal

def to_decimal(valor):
    if valor is None:
        return Decimal("0.00")
    return Decimal(str(valor))


def calcular_total_estancia(
    fecha_entrada,
    fecha_salida,
    hora_salida=None,
    precio_dia=0,
    importe_extras=0,
    importe_camaras=0,
    importe_transporte=0,
    importe_veterinario=0,
):
    dias = calcular_num_dias(
        fecha_entrada,
        fecha_salida,
        hora_salida
    )

    precio_dia = to_decimal(precio_dia)
    importe_extras = to_decimal(importe_extras)
    importe_camaras = to_decimal(importe_camaras)
    importe_transporte = to_decimal(importe_transporte)
    importe_veterinario = to_decimal(importe_veterinario)

    subtotal = Decimal(dias) * precio_dia

    total = (
        subtotal
        + importe_extras
        + importe_camaras
        + importe_transporte
        + importe_veterinario
    )

    return {
        "num_dias": dias,
        "subtotal": subtotal,
        "total": total,
    }