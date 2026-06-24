from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import get_db

from app.models.clientes import Cliente
from app.models.mascotas import Mascota
from app.models.habitacion import Habitacion
from app.models.estancia import Estancia

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/kpis")
def obtener_kpis(db: Session = Depends(get_db)):

    hoy = date.today()

    total_clientes = db.query(Cliente).count()

    total_mascotas = db.query(Mascota).count()

    total_habitaciones = db.query(Habitacion).count()

    mascotas_alojadas = db.query(Estancia).filter(
        Estancia.fecha_entrada <= hoy,
        Estancia.fecha_salida >= hoy
    ).count()

    habitaciones_libres = max(
        total_habitaciones - mascotas_alojadas,
        0
    )

    ocupacion = 0

    if total_habitaciones > 0:
        ocupacion = round(
            (mascotas_alojadas / total_habitaciones) * 100
        )

    entradas_hoy_detalle = db.query(Estancia).filter(
        func.date(Estancia.fecha_entrada) == hoy
    ).all()

    salidas_hoy_detalle = db.query(Estancia).filter(
        func.date(Estancia.fecha_salida) == hoy
    ).all()

    entradas_hoy = [
        {
            "mascota": e.mascota.nombre if e.mascota else "Sin mascota",
            "habitacion": e.habitacion.codigo if e.habitacion else None,
        }
        for e in entradas_hoy_detalle
    ]

    salidas_hoy = [
        {
            "mascota": e.mascota.nombre if e.mascota else "Sin mascota",
            "habitacion": e.habitacion.codigo if e.habitacion else None,
        }
        for e in salidas_hoy_detalle
    ]

    actividad_hoy = []

    

    for estancia in entradas_hoy_detalle:
        actividad_hoy.append({
            "tipo": "Entrada",
            "mascota": estancia.mascota.nombre if estancia.mascota else "Sin mascota",
            "habitacion": estancia.habitacion.codigo if estancia.habitacion else "-"
        })

    for estancia in salidas_hoy_detalle:
        actividad_hoy.append({
            "tipo": "Salida",
            "mascota": estancia.mascota.nombre if estancia.mascota else "Sin mascota",
            "habitacion": estancia.habitacion.codigo if estancia.habitacion else "-"
        })

    return {
        "total_clientes": total_clientes,
        "total_mascotas": total_mascotas,
        "capacidad_total": total_habitaciones,
        "habitaciones_libres": habitaciones_libres,
        "estancias_activas": mascotas_alojadas,
        "ocupacion": ocupacion,

        "total_entradas_hoy": len(entradas_hoy),
        "total_salidas_hoy": len(salidas_hoy),

        "entradas_hoy": entradas_hoy,
        "salidas_hoy": salidas_hoy,
        "actividad_hoy": actividad_hoy,

        "proximas_reservas": [],
        "ocupacion_7_dias": [],
        "ocupacion_grupos": [],
        "avisos": [],
        "ingresos_mes": 0,
    }