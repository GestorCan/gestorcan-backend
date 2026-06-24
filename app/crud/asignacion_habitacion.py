from sqlalchemy.orm import Session

from app.models.asignacion_habitacion import AsignacionHabitacion


def crear_asignacion_habitacion(db: Session, datos):
    nueva = AsignacionHabitacion(**datos.dict())

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


def listar_asignaciones_habitacion(db: Session):
    return db.query(AsignacionHabitacion)\
        .order_by(AsignacionHabitacion.fecha_entrada.desc())\
        .all()


def listar_asignaciones_activas(db: Session):
    return db.query(AsignacionHabitacion)\
        .filter(AsignacionHabitacion.activa == True)\
        .all()