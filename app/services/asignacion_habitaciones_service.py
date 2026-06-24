from sqlalchemy.orm import Session

from app.models.habitacion import Habitacion
from app.models.asignacion_habitacion import AsignacionHabitacion


PRIORIDAD_HABITACIONES = {
    "pequeño": ["pequeña", "mediana", "grande"],
    "mediano": ["mediana", "grande"],
    "grande": ["grande"],
    "gigante": "grande",
    "muy grande": "grande",
}


def obtener_ocupacion(db: Session, habitacion_id: int):

    return db.query(AsignacionHabitacion)\
        .filter(
            AsignacionHabitacion.habitacion_id == habitacion_id,
            AsignacionHabitacion.activa == True
        )\
        .count()


def normalizar_tamano_mascota(valor: str):

    if not valor:
        return None

    valor = valor.lower().strip()

    equivalencias = {
        "pequeña": "pequeño",
        "pequeño": "pequeño",
        "pequena": "pequeño",
        "pequeno": "pequeño",

        "mediana": "mediano",
        "mediano": "mediano",

        "grande": "grande",
        "gigante": "grande",
        "muy grande": "grande",
    }

    return equivalencias.get(valor)


def sugerir_habitacion(
    db: Session,
    residencia_id: int,
    tamano_mascota: str
):

    tamano_mascota = normalizar_tamano_mascota(tamano_mascota)

    if not tamano_mascota:
        return {
            "tipo": "error",
            "mensaje": "Tamaño de mascota no válido"
        }

    grupos_prioridad = PRIORIDAD_HABITACIONES.get(
        tamano_mascota,
        []
    )

    if not grupos_prioridad:
        return {
            "tipo": "error",
            "mensaje": "No hay prioridad definida para este tamaño"
        }

    # =====================================================
    # 1. Buscar libres
    # =====================================================

    for grupo in grupos_prioridad:

        habitaciones = db.query(Habitacion)\
            .filter(
                Habitacion.residencia_id == residencia_id,
                Habitacion.grupo == grupo,
                Habitacion.activa == True
            )\
            .all()

        for h in habitaciones:

            ocupadas = obtener_ocupacion(db, h.id)

            if ocupadas == 0:

                return {
                    "tipo": "asignacion_directa",
                    "habitacion": {
                        "id": h.id,
                        "nombre": h.nombre,
                        "grupo": h.grupo,
                        "ocupadas": ocupadas,
                        "capacidad": h.capacidad
                    }
                }

    # =====================================================
    # 2. Buscar parciales compatibles
    # =====================================================

    grupo_original = grupos_prioridad[0]

    habitaciones = db.query(Habitacion)\
        .filter(
            Habitacion.residencia_id == residencia_id,
            Habitacion.grupo == grupo_original,
            Habitacion.permite_compartir == True,
            Habitacion.activa == True
        )\
        .all()

    for h in habitaciones:

        ocupadas = obtener_ocupacion(db, h.id)

        if ocupadas > 0 and ocupadas < h.capacidad:

            return {
                "tipo": "confirmar_compartida",
                "mensaje": (
                    "Existe habitación parcialmente ocupada. "
                    "¿Deseas compartir?"
                ),
                "habitacion": {
                    "id": h.id,
                    "nombre": h.nombre,
                    "grupo": h.grupo,
                    "ocupadas": ocupadas,
                    "capacidad": h.capacidad
                }
            }

    return {
        "tipo": "sin_disponibilidad",
        "mensaje": "No hay habitaciones disponibles"
    }


def asignar_habitacion_estancia(
    db: Session,
    estancia_id: int,
    mascota_id: int,
    fecha_entrada,
    fecha_salida,
    confirmar_compartida=False
):

    from app.models.mascotas import Mascota

    mascota = db.query(Mascota)\
        .filter(Mascota.id == mascota_id)\
        .first()

    if not mascota:
        return {
            "ok": False,
            "mensaje": "Mascota no encontrada"
        }

    residencia_id = 1  # provisional

    sugerencia = sugerir_habitacion(
        db=db,
        residencia_id=residencia_id,
        tamano_mascota=mascota.tamano
    )

    tipo = sugerencia.get("tipo")

    if tipo == "sin_disponibilidad":
        return sugerencia

    if tipo == "error":
        return sugerencia

    habitacion = sugerencia.get("habitacion")

    if not habitacion:
        return {
            "ok": False,
            "mensaje": "No se pudo determinar habitación"
        }

    if tipo == "confirmar_compartida" and not confirmar_compartida:

        return {
            "ok": False,
            "requiere_confirmacion": True,
            "sugerencia": sugerencia
        }

    nueva = AsignacionHabitacion(
        estancia_id=estancia_id,
        mascota_id=mascota_id,
        habitacion_id=habitacion["id"],
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        activa=True
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {
        "ok": True,
        "mensaje": "Habitación asignada correctamente",
        "habitacion": habitacion,
        "asignacion_id": nueva.id
    }



def confirmar_asignacion_habitacion(db: Session, datos):

    habitacion = db.query(Habitacion)\
        .filter(Habitacion.id == datos.habitacion_id)\
        .first()

    if not habitacion:
        return {
            "ok": False,
            "mensaje": "Habitación no encontrada"
        }

    ocupadas = obtener_ocupacion(db, habitacion.id)

    if ocupadas >= habitacion.capacidad:
        return {
            "ok": False,
            "mensaje": "La habitación ya está completa"
        }

    if ocupadas > 0 and not habitacion.permite_compartir:
        return {
            "ok": False,
            "mensaje": "La habitación no permite compartir"
        }

    if ocupadas > 0 and not datos.confirmar_compartida:
        return {
            "ok": False,
            "requiere_confirmacion": True,
            "mensaje": "La habitación está parcialmente ocupada. Debes confirmar habitación compartida"
        }

    nueva = AsignacionHabitacion(
        estancia_id=datos.estancia_id,
        mascota_id=datos.mascota_id,
        habitacion_id=datos.habitacion_id,
        fecha_entrada=datos.fecha_entrada,
        fecha_salida=datos.fecha_salida,
        activa=True
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {
        "ok": True,
        "mensaje": "Habitación asignada correctamente",
        "asignacion_id": nueva.id,
        "habitacion": {
            "id": habitacion.id,
            "nombre": habitacion.nombre,
            "grupo": habitacion.grupo,
            "ocupadas": ocupadas + 1,
            "capacidad": habitacion.capacidad
        }
    }