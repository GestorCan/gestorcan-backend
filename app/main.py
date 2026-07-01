from datetime import date, timedelta
import os

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db

# Routers
from app.routers import (
    mascotas,
    residencias,
    estancias,
    tarifas,
    albaranes,
    clientes,
    dashboard_clientes,
    dashboard_mascotas,
    habitaciones,
    asignaciones_habitacion,
    dashboard as dashboard_router,
    ocupacion,
    gastos,
    proveedores,
    tipos_gasto,
    facturas_router,
    verifactu,
)

from app.routers.fiscal import fiscal

# Modelos
from app.models.clientes import Cliente
from app.models.mascotas import Mascota
from app.models.estancia import Estancia
from app.models.factura import Factura
from app.models.habitacion import Habitacion
from app.models.asignacion_habitacion import AsignacionHabitacion
from app.models.tarifa_model import Tarifa
from app.models.gasto import Gasto
from app.models.proveedor import Proveedor
from app.models.tipo_gasto import TipoGasto
from app.models.residencias import Residencia
from app.models.contador_factura import ContadorFactura
from app.models.verifactu_registro import VeriFactuRegistro
from app.services.scheduler_service import iniciar_scheduler, parar_scheduler
from app.routers import pruebas



app = FastAPI()

@app.on_event("startup")
def startup_event():
    iniciar_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    parar_scheduler()

app.include_router(pruebas.router)

Base.metadata.create_all(bind=engine)





app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app/
ROOT_DIR = os.path.dirname(BASE_DIR)  # gestorcan-backend/

STATIC_PATH = os.path.join(ROOT_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home():
    return RedirectResponse(
        url="/Dashboard"
    )

@app.get("/admin/test-autoreport")
def test_autoreport():
    from app.services.autoreport_service import ejecutar_autoreport

    ejecutar_autoreport()

    return {
        "ok": True,
        "mensaje": "Autoreport ejecutado"
    }






@app.get("/config-residencia",
    response_class=HTMLResponse
)
def config_residencia_html():

    with open(
        "frontend/config_residencia.html",
        encoding="utf-8"
    ) as f:

        return f.read()

@app.get("/planning-barras", response_class=HTMLResponse)
def planning_barras_html():

    with open(
        "frontend/planning_barras.html",
        encoding="utf-8"
    ) as f:

        return f.read()



@app.get("/planning-habitaciones", response_class=HTMLResponse)
def planning_habitaciones_html():

    with open(
        "frontend/planning_habitaciones.html",
        encoding="utf-8"
    ) as f:
        return f.read()





@app.get("/dashboard-habitaciones", response_class=HTMLResponse)
def dashboard_habitaciones():

    with open(
        "frontend/habitaciones_dashboard.html",
        encoding="utf-8"
    ) as f:

        return f.read()






@app.get("/Dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    hoy = date.today()

    total_clientes = db.query(Cliente).count()
    total_mascotas = db.query(Mascota).count()

    capacidad_total = (
        db.query(Habitacion)
        .filter(Habitacion.activa == True)
        .count()
    )

    estancias_activas = (
        db.query(Estancia)
        .filter(
            Estancia.fecha_entrada <= hoy,
            Estancia.fecha_salida >= hoy
        )
        .count()
    )

    ocupacion = 0

    if capacidad_total > 0:
        ocupacion = round((estancias_activas / capacidad_total) * 100)

    entradas_hoy_obj = (
        db.query(Estancia)
        .filter(Estancia.fecha_entrada == hoy)
        .all()
    )

    salidas_hoy_obj = (
        db.query(Estancia)
        .filter(Estancia.fecha_salida == hoy)
        .all()
    )

    entradas_hoy = [
        {
            "mascota": e.mascota.nombre if e.mascota else "Sin mascota",
            "habitacion": e.habitacion if e.habitacion else None,
        }
        for e in entradas_hoy_obj
    ]

    salidas_hoy = [
        {
            "mascota": e.mascota.nombre if e.mascota else "Sin mascota",
            "habitacion": e.habitacion if e.habitacion else None,
        }
        for e in salidas_hoy_obj
    ]

    ingresos_mes = 0

    estancias_mes = (
        db.query(Estancia)
        .filter(
            extract("month", Estancia.fecha_entrada) == hoy.month,
            extract("year", Estancia.fecha_entrada) == hoy.year
        )
        .all()
    )

    for e in estancias_mes:
        ingresos_mes += float(e.total or 0)

    datos = {
        "total_clientes": total_clientes,
        "total_mascotas": total_mascotas,
        "estancias_activas": estancias_activas,
        "ocupacion": ocupacion,
        "capacidad_total": capacidad_total,

        "entradas_hoy": entradas_hoy,
        "salidas_hoy": salidas_hoy,

        "total_entradas_hoy": len(entradas_hoy),
        "total_salidas_hoy": len(salidas_hoy),

        "habitaciones_libres": capacidad_total - estancias_activas,
        "ingresos_mes": round(ingresos_mes, 2),

        # Para que no fallen las tarjetas vacías
        "proximas_reservas": [],
        "avisos": [],
        "ocupacion_7_dias": [],
        "ocupacion_grupos": [],
    }

    modulos = [
        {
            "nombre": "Listado de estancias",
            "descripcion": "Buscar, editar, cobrar, facturar y exportar estancias",
            "url": "/estancias/listado",
            "icono": "clipboard-list",
        },
        {
            "nombre": "Nueva estancia",
            "descripcion": "Registrar una nueva entrada",
            "url": "/estancias/form",
            "icono": "plus-circle",
        },
        {
            "nombre": "Habitaciones",
            "descripcion": "Ocupación, estados y planificación visual",
            "icono": "bed-double",
            "url": "/dashboard-habitaciones"
        },
        {
            "nombre": "Residencia",
            "descripcion": "Configuración general y personalización",
            "icono": "building-2",
            "url": "/config-residencia"
        },

    ]

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "titulo": "Dashboard",
            "datos": datos,
            "modulos": modulos,
        }
    )

app.include_router(clientes.router)
app.include_router(mascotas.router)
app.include_router(residencias.router)
app.include_router(estancias.router)
app.include_router(albaranes.router)
app.include_router(tarifas.router)
app.include_router(facturas_router.router)

app.include_router(dashboard_clientes.router)
app.include_router(dashboard_mascotas.router)

app.include_router(habitaciones.router)
app.include_router(asignaciones_habitacion.router)
app.include_router(dashboard_router.router)

app.include_router(ocupacion.router)
app.include_router(gastos.router)
app.include_router(proveedores.router)
app.include_router(tipos_gasto.router)


app.include_router(pruebas.router)


# FISCAL
app.include_router(fiscal.router,prefix="/fiscal",tags=["Fiscal"])

# VERIFACTU
app.include_router(verifactu.router,prefix="/fiscal/verifactu",tags=["VeriFactu"])

app.include_router(verifactu.router)





def get_dashboard_data():
    db: Session = SessionLocal()

    try:
        # 🔹 Totales
        total_clientes = db.query(Cliente).count()
        total_mascotas = db.query(Mascota).count()

        # 🔹 Estancias activas (hoy)
        hoy = date.today()

        estancias_activas = db.query(Estancia).filter(
            Estancia.fecha_entrada <= hoy,
            Estancia.fecha_salida >= hoy
        ).count()

        total_habitaciones = db.query(Habitacion).count()

        capacidad_total = total_habitaciones

        ocupacion = 0
        habitaciones_libres = max(
            capacidad_total - estancias_activas,
            0
        )
        if capacidad_total > 0:
            ocupacion = round((estancias_activas / capacidad_total) * 100)

        hoy = date.today()

        # Entradas de hoy
        entradas_hoy = db.query(Estancia).filter(
            Estancia.fecha_entrada == hoy
        ).all()

        # Salidas de hoy
        salidas_hoy = db.query(Estancia).filter(
            Estancia.fecha_salida == hoy
        ).all()
        inicio_mes = hoy.replace(day=1)

        ingresos_mes = db.query(
            func.coalesce(func.sum(Estancia.total), 0)
        ).filter(
            Estancia.fecha_entrada >= inicio_mes,
            Estancia.fecha_entrada <= hoy
        ).scalar()

        avisos = []

        # Ocupación alta
        if ocupacion >= 80:
            avisos.append({
                "tipo": "warning",
                "texto": f"Ocupación alta: {ocupacion}%"
            })

        # Entradas hoy
        if len(entradas_hoy) > 0:
            avisos.append({
                "tipo": "info",
                "texto": f"{len(entradas_hoy)} entrada(s) programada(s) hoy"
            })

        # Salidas hoy
        if len(salidas_hoy) > 0:
            avisos.append({
                "tipo": "info",
                "texto": f"{len(salidas_hoy)} salida(s) prevista(s) hoy"
            })

        # Próximas reservas
        proximas_reservas = db.query(Estancia).filter(
            Estancia.fecha_entrada > hoy
        ).order_by(
            Estancia.fecha_entrada.asc()
        ).limit(5).all()



        ocupacion_7_dias = []

        for i in range(7):

            fecha = hoy + timedelta(days=i)

            ocupadas = db.query(Estancia).filter(
                Estancia.fecha_entrada <= fecha,
                Estancia.fecha_salida >= fecha
            ).count()

            porcentaje = 0

            if capacidad_total > 0:
                porcentaje = round(
                    (ocupadas / capacidad_total) * 100
                )

            ocupacion_7_dias.append({
                "fecha": fecha.strftime("%d/%m"),
                "ocupacion": porcentaje
            })

        # =====================================================
        # OCUPACIÓN POR GRUPOS
        # =====================================================

        ocupacion_grupos = []

        grupos = db.query(Habitacion.grupo).distinct().all()

        for grupo_row in grupos:

            grupo = grupo_row[0]

            total_grupo = db.query(Habitacion).filter(
                Habitacion.grupo == grupo
            ).count()

            ocupadas = db.query(AsignacionHabitacion).join(
                Habitacion,
                Habitacion.id == AsignacionHabitacion.habitacion_id
            ).filter(
                Habitacion.grupo == grupo,
                AsignacionHabitacion.fecha_entrada <= hoy,
                AsignacionHabitacion.fecha_salida >= hoy
            ).count()

            porcentaje = 0

            if total_grupo > 0:
                porcentaje = round(
                    (ocupadas / total_grupo) * 100
                )

            ocupacion_grupos.append({
                "grupo": grupo,
                "ocupacion": porcentaje
            })







        return {
            "total_clientes": total_clientes,
            "total_mascotas": total_mascotas,
            "estancias_activas": estancias_activas,
            "capacidad_total": capacidad_total,
            "ocupacion": ocupacion,

            "habitaciones_libres": habitaciones_libres,
            "ingresos_mes": round(float(ingresos_mes), 2),
            "total_entradas_hoy": len(entradas_hoy),
            "total_salidas_hoy": len(salidas_hoy),

            "avisos": avisos,
            "proximas_reservas": [
                {
                    "mascota": e.mascota.nombre if e.mascota else "Sin mascota",
                    "habitacion": e.habitacion or "",
                    "entrada": e.fecha_entrada.strftime("%d/%m/%Y")
                }
                for e in proximas_reservas
            ],

            "entradas_hoy": [
                {
                    "mascota": e.mascota.nombre if e.mascota else "Sin mascota",
                    "habitacion": e.habitacion or ""
                }
                for e in entradas_hoy
            ],

            "salidas_hoy": [
                {
                    "mascota": e.mascota.nombre if e.mascota else "Sin mascota",
                    "habitacion": e.habitacion or ""
                }
                for e in salidas_hoy
            ],
            "ocupacion_7_dias": ocupacion_7_dias,
            "ocupacion_grupos": ocupacion_grupos,


        }

    finally:
        db.close()

@app.get("/dashboard/albaranes", response_class=HTMLResponse)
def dashboard_albaranes(request: Request):

    return templates.TemplateResponse(
        request,
        "albaranes/dashboard.html",
        {}
    )



@app.get("/dashboard/informes", response_class=HTMLResponse)
def dashboard_informes(request: Request):

    db = SessionLocal()

    hoy = date.today()
    hace_30 = hoy - timedelta(days=30)

    # =========================
    # OCUPACIÓN MEDIA
    # =========================

    total_habitaciones = db.query(Habitacion).count()

    estancias_activas = db.query(Estancia).filter(
        Estancia.fecha_entrada <= hoy,
        Estancia.fecha_salida >= hoy
    ).count()

    ocupacion_media = 0

    if total_habitaciones > 0:
        ocupacion_media = round(
            (estancias_activas / total_habitaciones) * 100
        )

    # =========================
    # INGRESOS MES
    # =========================

    ingresos = db.query(
        func.sum(Factura.total)
    ).scalar() or 0

    # =========================
    # ESTANCIAS MES
    # =========================

    estancias_mes = db.query(Estancia).filter(
        Estancia.fecha_entrada >= hace_30
    ).count()

    # =========================
    # CLIENTES ACTIVOS
    # =========================

    clientes_activos = db.query(
        Cliente.id
    ).join(
        Estancia
    ).filter(
        Estancia.fecha_entrada >= hace_30
    ).distinct().count()



    return templates.TemplateResponse(
        request,
        "informes/dashboard.html",
        {
            "ocupacion_media": ocupacion_media,
            "ingresos": ingresos,
            "estancias_mes": estancias_mes,
            "clientes_activos": clientes_activos
        }
    )
