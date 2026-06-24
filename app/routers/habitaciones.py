## app/routers/habitaciones.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.habitacion import (HabitacionCreate, HabitacionUpdate, HabitacionResponse, HabitacionDashboardResponse, GenerarHabitacionesRequest,)
from app.crud.habitaciones import (crear_habitacion, obtener_habitaciones, obtener_habitacion, actualizar_habitacion, eliminar_habitacion, obtener_dashboard_habitaciones, obtener_dashboard_por_grupos,generar_habitaciones_residencia,)
from app.schemas.sugerencia_habitacion import (SugerirHabitacionRequest)
from app.services.asignacion_habitaciones_service import (sugerir_habitacion)

router = APIRouter(
    prefix="/habitaciones",
    tags=["Habitaciones"]
)
from app.models.habitacion import Habitacion
from datetime import date, timedelta
from app.models.asignacion_habitacion import AsignacionHabitacion
from app.models.mascotas import Mascota
from app.models.clientes import Cliente
from app.models.estancia import Estancia
from datetime import date
from sqlalchemy.orm import joinedload

from app.models.estancia import Estancia




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/api/estado")
def estado_habitaciones(
    fecha: date | None = None,
    db: Session = Depends(get_db)
):

    fecha_consulta = fecha or date.today()

    habitaciones = (
        db.query(Habitacion)
        .filter(Habitacion.activa == True)
        .order_by(Habitacion.grupo, Habitacion.nombre)
        .all()
    )

    estancias_activas = (
        db.query(Estancia)
        .options(
            joinedload(Estancia.mascota),
            joinedload(Estancia.cliente)
        )
        .filter(
            Estancia.fecha_entrada <= fecha_consulta,
            Estancia.fecha_salida >= fecha_consulta
        )
        .all()
    )

    ocupadas = {}

    for e in estancias_activas:
        if not e.habitacion:
            continue

        clave = str(e.habitacion).strip().upper()

        if clave not in ocupadas:
            ocupadas[clave] = []

        ocupadas[clave].append(e)

    resultado = []

    for h in habitaciones:
        clave = str(h.nombre).strip().upper()
        estancias = ocupadas.get(clave, [])

        estado = "libre"
        mascota = None
        cliente = None

        if len(estancias) > 0:
            estado = "ocupada"

            primera = estancias[0]

            mascota = primera.mascota.nombre if primera.mascota else None

            if primera.cliente:
                cliente = f"{primera.cliente.nombre} {primera.cliente.apellidos or ''}".strip()

        resultado.append({
            "id": h.id,
            "nombre": h.nombre,
            "grupo": h.grupo,
            "estado": estado,
            "mascota": mascota,
            "cliente": cliente,
            "ocupantes": len(estancias)
        })

    return resultado

@router.get("/planning-barras")
def planning_barras(
    residencia_id: int = 1,
    fecha_inicio: date = date.today(),
    dias: int = 15,
    db: Session = Depends(get_db)
):

    habitaciones = db.query(Habitacion)\
        .filter(
            Habitacion.residencia_id == residencia_id,
            Habitacion.activa == True
        )\
        .order_by(Habitacion.grupo, Habitacion.nombre)\
        .all()

    fecha_fin = fecha_inicio + timedelta(days=dias)

    resultado = []

    for habitacion in habitaciones:

        asignaciones = db.query(AsignacionHabitacion)\
            .filter(
                AsignacionHabitacion.habitacion_id == habitacion.id,
                AsignacionHabitacion.activa == True,
                AsignacionHabitacion.fecha_salida >= fecha_inicio,
                AsignacionHabitacion.fecha_entrada <= fecha_fin
            )\
            .all()

        reservas = []

        for a in asignaciones:

            mascota = db.query(Mascota) \
                .filter(Mascota.id == a.mascota_id) \
                .first()

            estancia = db.query(Estancia) \
                .filter(Estancia.id == a.estancia_id) \
                .first()

            cliente_nombre = "Cliente"

            if estancia:
                cliente = db.query(Cliente) \
                    .filter(Cliente.id == estancia.cliente_id) \
                    .first()

                if cliente:
                    cliente_nombre = (
                        f"{cliente.nombre} {cliente.apellidos}"
                    ).strip()

            inicio_offset = (
                a.fecha_entrada - fecha_inicio
            ).days

            fin_offset = (
                a.fecha_salida - fecha_inicio
            ).days

            reservas.append({
                "asignacion_id": a.id,

                "mascota": mascota.nombre if mascota else "Mascota",
                "cliente": cliente_nombre,
                "inicio": a.fecha_entrada.isoformat(),
                "fin": a.fecha_salida.isoformat(),

                "inicio_offset": inicio_offset,
                "fin_offset": fin_offset,

                "duracion": max(
                    1,
                    fin_offset - inicio_offset
                )
            })

        resultado.append({
            "habitacion_id": habitacion.id,
            "habitacion": habitacion.nombre,
            "grupo": habitacion.grupo,
            "reservas": reservas
        })

    return {
        "fecha_inicio": fecha_inicio.isoformat(),
        "dias": dias,
        "habitaciones": resultado
    }




@router.post("/sugerir")
def sugerir(
    datos: SugerirHabitacionRequest,
    db: Session = Depends(get_db)
):

    return sugerir_habitacion(
        db=db,
        residencia_id=datos.residencia_id,
        tamano_mascota=datos.tamano_mascota
    )


@router.post("/", response_model=HabitacionResponse)
def crear(datos: HabitacionCreate, db: Session = Depends(get_db)):
    return crear_habitacion(db, datos)


@router.get("/", response_model=list[HabitacionResponse])
def listar(db: Session = Depends(get_db)):
    return obtener_habitaciones(db)


@router.get("/dashboard", response_model=list[HabitacionDashboardResponse])
def dashboard(db: Session = Depends(get_db)):
    return obtener_dashboard_habitaciones(db)

@router.get("/dashboard/grupos")
def dashboard_grupos(db: Session = Depends(get_db)):
    return obtener_dashboard_por_grupos(db)


@router.post("/residencia/{residencia_id}/generar")
def generar_habitaciones(
    residencia_id: int,
    datos: GenerarHabitacionesRequest,
    db: Session = Depends(get_db)
):
    return generar_habitaciones_residencia(
        db=db,
        residencia_id=residencia_id,
        datos=datos
    )


@router.get("/planning")
def planning_habitaciones(
    residencia_id: int = 1,
    fecha_inicio: date = date.today(),
    dias: int = 15,
    db: Session = Depends(get_db)
):

    habitaciones = db.query(Habitacion)\
        .filter(
            Habitacion.residencia_id == residencia_id,
            Habitacion.activa == True
        )\
        .order_by(Habitacion.grupo, Habitacion.nombre)\
        .all()

    fechas = [
        fecha_inicio + timedelta(days=i)
        for i in range(dias)
    ]

    resultado = []

    for habitacion in habitaciones:

        fila = {
            "habitacion_id": habitacion.id,
            "habitacion": habitacion.nombre,
            "grupo": habitacion.grupo,
            "capacidad": habitacion.capacidad,
            "dias": []
        }

        for fecha in fechas:

            ocupadas = db.query(AsignacionHabitacion)\
                .filter(
                    AsignacionHabitacion.habitacion_id == habitacion.id,
                    AsignacionHabitacion.activa == True,
                    AsignacionHabitacion.fecha_entrada <= fecha,
                    AsignacionHabitacion.fecha_salida > fecha
                )\
                .count()

            if ocupadas == 0:
                estado = "libre"
            elif ocupadas < habitacion.capacidad:
                estado = "parcial"
            else:
                estado = "ocupada"

            fila["dias"].append({
                "fecha": fecha.isoformat(),
                "estado": estado,
                "ocupadas": ocupadas,
                "capacidad": habitacion.capacidad
            })

        resultado.append(fila)

    return {
        "residencia_id": residencia_id,
        "fecha_inicio": fecha_inicio.isoformat(),
        "dias": dias,
        "planning": resultado
    }




@router.get("/{habitacion_id}", response_model=HabitacionResponse)
def detalle(habitacion_id: int, db: Session = Depends(get_db)):
    habitacion = obtener_habitacion(db, habitacion_id)

    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")

    return habitacion


@router.put("/{habitacion_id}", response_model=HabitacionResponse)
def editar(
    habitacion_id: int,
    datos: HabitacionUpdate,
    db: Session = Depends(get_db)
):
    habitacion = actualizar_habitacion(db, habitacion_id, datos)

    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")

    return habitacion


@router.delete("/{habitacion_id}")
def borrar(habitacion_id: int, db: Session = Depends(get_db)):
    ok = eliminar_habitacion(db, habitacion_id)

    if not ok:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")

    return {"ok": True}