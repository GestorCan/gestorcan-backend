from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.schemas.asignacion_habitacion import (
    AsignacionHabitacionCreate,
    AsignacionHabitacionResponse,
)

from app.crud.asignacion_habitacion import (
    crear_asignacion_habitacion,
    listar_asignaciones_habitacion,
    listar_asignaciones_activas,
)

from app.schemas.asignacion_habitacion import (
    AsignacionHabitacionCreate,
    AsignacionHabitacionResponse,
    ConfirmarAsignacionHabitacionRequest,
)

from app.services.asignacion_habitaciones_service import (
    confirmar_asignacion_habitacion
)


router = APIRouter(
    prefix="/asignaciones-habitacion",
    tags=["Asignaciones Habitación"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





@router.post("/confirmar")
def confirmar_asignacion(
    datos: ConfirmarAsignacionHabitacionRequest,
    db: Session = Depends(get_db)
):
    return confirmar_asignacion_habitacion(db, datos)







@router.post("/", response_model=AsignacionHabitacionResponse)
def crear(datos: AsignacionHabitacionCreate, db: Session = Depends(get_db)):
    return crear_asignacion_habitacion(db, datos)


@router.get("/", response_model=list[AsignacionHabitacionResponse])
def listar(db: Session = Depends(get_db)):
    return listar_asignaciones_habitacion(db)


@router.get("/activas", response_model=list[AsignacionHabitacionResponse])
def activas(db: Session = Depends(get_db)):
    return listar_asignaciones_activas(db)