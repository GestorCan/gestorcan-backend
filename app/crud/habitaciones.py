# app/crud/crud_habitaciones.py

from sqlalchemy.orm import Session

from app.models.habitacion import Habitacion
from app.constants.habitaciones import (
    COLORES_ESTADO_HABITACION,
    ICONOS_ESTADO_HABITACION)

from app.models.asignacion_habitacion import AsignacionHabitacion





def crear_habitacion(db: Session, datos):
    nueva = Habitacion(**datos.dict())

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


def obtener_habitaciones(db: Session):
    return db.query(Habitacion)\
        .order_by(Habitacion.nombre)\
        .all()


def obtener_habitacion(db: Session, habitacion_id: int):
    return db.query(Habitacion)\
        .filter(Habitacion.id == habitacion_id)\
        .first()


def actualizar_habitacion(db: Session, habitacion_id: int, datos):
    habitacion = obtener_habitacion(db, habitacion_id)

    if not habitacion:
        return None

    for key, value in datos.dict().items():
        setattr(habitacion, key, value)

    db.commit()
    db.refresh(habitacion)

    return habitacion


def eliminar_habitacion(db: Session, habitacion_id: int):
    habitacion = obtener_habitacion(db, habitacion_id)

    if not habitacion:
        return None

    db.delete(habitacion)
    db.commit()

    return True

def obtener_dashboard_habitaciones(db: Session):

    habitaciones = db.query(Habitacion)\
        .filter(Habitacion.activa == True)\
        .order_by(Habitacion.grupo, Habitacion.nombre)\
        .all()

    resultado = []

    for h in habitaciones:

        ocupadas = db.query(AsignacionHabitacion)\
            .filter(
                AsignacionHabitacion.habitacion_id == h.id,
                AsignacionHabitacion.activa == True
            )\
            .count()

        if ocupadas == 0:
            estado_real = "libre"
        elif ocupadas < h.capacidad:
            estado_real = "parcial"
        else:
            estado_real = "ocupada"

        color = COLORES_ESTADO_HABITACION.get(estado_real, "#999999")
        icono = ICONOS_ESTADO_HABITACION.get(estado_real, "❔")

        item = {
            "id": h.id,
            "nombre": h.nombre,
            "grupo": h.grupo,
            "capacidad": h.capacidad,
            "estado": estado_real,

            "permite_camara": h.permite_camara,
            "permite_compartir": h.permite_compartir,

            "color": color,
            "icono": icono,

            "texto_estado": estado_real.capitalize(),
            "texto_capacidad": f"{ocupadas} / {h.capacidad}",

            "observaciones": h.observaciones
        }

        resultado.append(item)

    return resultado

def obtener_dashboard_por_grupos(db: Session):

    habitaciones = db.query(Habitacion)\
        .filter(Habitacion.activa == True)\
        .order_by(Habitacion.nombre)\
        .all()

    resultado = {
        "pequeña": [],
        "mediana": [],
        "grande": []
    }

    for h in habitaciones:

        ocupadas = db.query(AsignacionHabitacion)\
            .filter(
                AsignacionHabitacion.habitacion_id == h.id,
                AsignacionHabitacion.activa == True
            )\
            .count()

        if ocupadas == 0:
            estado_real = "libre"

        elif ocupadas < h.capacidad:
            estado_real = "parcial"

        else:
            estado_real = "ocupada"

        color = COLORES_ESTADO_HABITACION.get(
            estado_real,
            "#999999"
        )

        icono = ICONOS_ESTADO_HABITACION.get(
            estado_real,
            "❔"
        )

        item = {
            "id": h.id,
            "nombre": h.nombre,
            "grupo": h.grupo,
            "capacidad": h.capacidad,
            "estado": estado_real,

            "permite_camara": h.permite_camara,
            "permite_compartir": h.permite_compartir,
            "activa": h.activa,

            "color": color,
            "icono": icono,

            "texto_estado": estado_real.capitalize(),
            "texto_capacidad": f"{ocupadas} / {h.capacidad}",

            "observaciones": h.observaciones,
        }

        if h.grupo in resultado:
            resultado[h.grupo].append(item)

    return resultado

def generar_habitaciones_residencia(db: Session, residencia_id: int, datos):

    creadas = []

    for numero in range(1, datos.cantidad + 1):

        nombre = f"{datos.prefijo}{numero:02d}"

        existe = db.query(Habitacion).filter(
            Habitacion.residencia_id == residencia_id,
            Habitacion.nombre == nombre
        ).first()

        if existe:
            continue

        nueva = Habitacion(
            residencia_id=residencia_id,
            nombre=nombre,
            grupo=datos.grupo,
            capacidad=datos.capacidad,
            permite_camara=datos.permite_camara,
            permite_compartir=datos.permite_compartir,
            estado="libre",
            activa=True
        )

        db.add(nueva)
        creadas.append(nueva)

    db.commit()

    return {
        "residencia_id": residencia_id,
        "creadas": len(creadas)
    }
