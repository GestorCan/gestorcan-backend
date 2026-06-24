# app/crud/estancias.py

from sqlalchemy.orm import Session
from app.models.estancia import Estancia
from app.schemas.estancia import EstanciaCreate, EstanciaUpdate
from app.services.estancias_calculos import calcular_total_estancia

from app.services.tarifas_service import obtener_precio_tarifa
from datetime import datetime


from datetime import time

def calcular_dias(fecha_entrada, fecha_salida, hora_salida=None):
    if not fecha_entrada or not fecha_salida:
        return 0

    dias = (fecha_salida - fecha_entrada).days

    if hora_salida:
        limite = time(12, 0)

        if hora_salida > limite:
            dias += 1

    return dias if dias > 0 else 0


def crear_estancia(db: Session, estancia: EstanciaCreate):

    datos = estancia.model_dump()

    dias = calcular_dias(
        estancia.fecha_entrada,
        estancia.fecha_salida,
        estancia.hora_salida
    )

    # 🔹 PRECIO DÍA
    precio_dia = obtener_precio_tarifa(
        "estancia_dia",
        estancia.tipo_precio_dia
    )

    subtotal = dias * precio_dia

    # 🔹 CÁMARAS
    importe_camaras = 0
    if estancia.camaras:
        precio = obtener_precio_tarifa("servicio", "camaras")
        importe_camaras = precio * dias

    # 🔹 EXTRAS
    importe_extras = 0
    if estancia.extras:
        precio = obtener_precio_tarifa("extra", estancia.extras)

        if estancia.extras == "pienso":
            importe_extras = precio * dias
        else:
            importe_extras = precio

    # 🔹 VETERINARIO
    importe_veterinario = 0
    if estancia.veterinario:
        importe_veterinario = obtener_precio_tarifa(
            "servicio",
            "veterinario"
        )

    # 🔹 TRANSPORTE
    importe_transporte = 0
    if estancia.transporte:
        precio_km = obtener_precio_tarifa("transporte_km", "km")
        kms = float(estancia.kilometros or 0)
        importe_transporte = kms * precio_km

    # 🔹 TOTAL
    total = (
        subtotal
        + importe_camaras
        + importe_extras
        + importe_veterinario
        + importe_transporte
    )

    datos["num_dias"] = dias
    datos["precio_dia"] = precio_dia
    datos["subtotal"] = subtotal
    datos["importe_camaras"] = importe_camaras
    datos["importe_extras"] = importe_extras
    datos["importe_veterinario"] = importe_veterinario
    datos["importe_transporte"] = importe_transporte
    datos["total"] = total

    # Este sí se elimina porque NO existe en modelo Estancia
    datos.pop("precio_km", None)

    nueva_estancia = Estancia(**datos)

    db.add(nueva_estancia)
    db.commit()
    db.refresh(nueva_estancia)

    return nueva_estancia



def obtener_estancias(db: Session):
    return db.query(Estancia).order_by(Estancia.fecha_entrada.desc()).all()


def obtener_estancia(db: Session, estancia_id: int):
    return db.query(Estancia).filter(Estancia.id == estancia_id).first()


def actualizar_estancia(db: Session, estancia_id: int, datos: EstanciaUpdate):
    estancia = obtener_estancia(db, estancia_id)
    kilometros: float | None = 0
    if not estancia:
        return None

    calculos = calcular_total_estancia(
        fecha_entrada=datos.fecha_entrada,
        fecha_salida=datos.fecha_salida,
        hora_salida=datos.hora_salida,
        precio_dia=datos.precio_dia,
        importe_extras=datos.importe_extras,
        importe_camaras=datos.importe_camaras,
        importe_transporte=datos.importe_transporte,
        importe_veterinario=datos.importe_veterinario,
    )

    for campo, valor in datos.model_dump().items():
        setattr(estancia, campo, valor)

    estancia.num_dias = calculos["num_dias"]
    estancia.subtotal = calculos["subtotal"]
    estancia.total = calculos["total"]

    db.commit()
    db.refresh(estancia)

    return estancia


def borrar_estancia(db: Session, estancia_id: int):
    estancia = obtener_estancia(db, estancia_id)

    if not estancia:
        return None

    db.delete(estancia)
    db.commit()

    return estancia