from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import date, timedelta, datetime
from app.database import SessionLocal
from app.models.estancia import Estancia
from app.models.habitacion import Habitacion
from datetime import date, timedelta
from sqlalchemy.orm import joinedload
from app.database import get_db

from datetime import date
from app.models.factura import Factura
from app.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook
from app.models.clientes import Cliente
from app.models.mascotas import Mascota
import re

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")




@router.get("/api/exportar-excel")
def exportar_excel(
    tipo: str,
    desde: str | None = None,
    hasta: str | None = None,
    db: Session = Depends(get_db)
):
    wb = Workbook()
    ws = wb.active

    if tipo == "clientes":
        ws.title = "Clientes"
        ws.append(["ID", "Nombre", "Apellidos", "DNI", "Teléfono", "Email"])

        clientes = db.query(Cliente).all()

        for c in clientes:
            ws.append([
                c.id,
                c.nombre,
                c.apellidos,
                c.dni,
                c.telefono,
                c.email
            ])

        filename = "clientes.xlsx"

    elif tipo == "mascotas":
        ws.title = "Mascotas"
        ws.append(["ID", "Nombre", "Raza", "Sexo", "Tamaño", "Cliente"])

        mascotas = db.query(Mascota).all()

        for m in mascotas:
            ws.append([
                m.id,
                m.nombre,
                m.raza,
                m.sexo,
                m.tamano,
                m.cliente.nombre if m.cliente else ""
            ])

        filename = "mascotas.xlsx"

    elif tipo == "estancias":
        ws.title = "Estancias"
        ws.append([
            "ID", "Cliente", "Mascota", "Entrada", "Salida",
            "Habitación", "Días", "Precio día", "Total", "Pagado", "Facturado"
        ])

        query = db.query(Estancia).options(
            joinedload(Estancia.cliente),
            joinedload(Estancia.mascota)
        )

        if desde:
            query = query.filter(Estancia.fecha_entrada >= date.fromisoformat(desde))

        if hasta:
            query = query.filter(Estancia.fecha_entrada <= date.fromisoformat(hasta))

        estancias = query.order_by(Estancia.fecha_entrada.desc()).all()

        for e in estancias:
            ws.append([
                e.id,
                f"{e.cliente.nombre} {e.cliente.apellidos or ''}" if e.cliente else "",
                e.mascota.nombre if e.mascota else "",
                e.fecha_entrada,
                e.fecha_salida,
                e.habitacion,
                e.num_dias,
                float(e.precio_dia or 0),
                float(e.total or 0),
                "Sí" if e.pagado else "No",
                "Sí" if e.facturado else "No",
            ])

        filename = "estancias_albaranes.xlsx"

    else:
        raise HTTPException(status_code=400, detail="Tipo de exportación no válido")

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/api/ocupacion-tipos")
def api_ocupacion_tipos(db: Session = Depends(get_db)):
    inicio = date.today()
    fin = inicio + timedelta(days=30)

    habitaciones = (
        db.query(Habitacion)
        .filter(Habitacion.activa == True)
        .all()
    )

    grupo_por_habitacion = {
        h.nombre.upper(): h.grupo
        for h in habitaciones
    }

    estancias = (
        db.query(Estancia)
        .filter(
            Estancia.fecha_entrada <= fin,
            Estancia.fecha_salida >= inicio
        )
        .all()
    )

    resultado = []

    for i in range(31):
        dia = inicio + timedelta(days=i)

        fila = {
            "fecha": dia.isoformat(),
            "grande": 0,
            "mediana": 0,
            "pequeña": 0,
            "gigante": 0,
        }

        for e in estancias:
            if not e.habitacion:
                continue

            if e.fecha_entrada <= dia <= e.fecha_salida:
                grupo = grupo_por_habitacion.get(e.habitacion.upper())

                if grupo in fila:
                    fila[grupo] += 1

        resultado.append(fila)

    return resultado



@router.get("/planner")
def planner_habitaciones(
    request: Request,
    fecha: str | None = None,
    db: Session = Depends(get_db)
):

    if fecha:
        fecha_inicio = datetime.strptime(fecha, "%Y-%m-%d").date()
    else:
        fecha_inicio = date.today()

    fecha_fin = fecha_inicio + timedelta(days=6)

    dias = [
        fecha_inicio + timedelta(days=i)
        for i in range(7)
    ]

    habitaciones = (
        db.query(Habitacion)
        .filter(Habitacion.activa == True)
        .order_by(Habitacion.grupo, Habitacion.nombre)
        .all()
    )

    estancias = (
        db.query(Estancia)
        .options(
            joinedload(Estancia.cliente),
            joinedload(Estancia.mascota)
        )
        .filter(
            Estancia.fecha_entrada <= fecha_fin,
            Estancia.fecha_salida >= fecha_inicio
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="ocupacion/planner.html",
        context={
            "habitaciones": habitaciones,
            "estancias": estancias,
            "dias": dias,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "timedelta": timedelta,
        }
    )
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def normalizar_habitacion(valor):
    if not valor:
        return ""

    valor = str(valor).strip().upper()

    match = re.match(r"^([A-Z]+)0*(\d+)$", valor)

    if match:
        letra = match.group(1)
        numero = int(match.group(2))
        return f"{letra}{numero:02d}"

    return valor
@router.get("/ocupacion")
def dashboard_ocupacion(
    request: Request,
    db: Session = Depends(get_db)
):
    fecha_str = request.query_params.get("fecha")

    if fecha_str:
        fecha_consulta = date.fromisoformat(fecha_str)
    else:
        fecha_consulta = date.today()

    habitaciones = (
        db.query(Habitacion)
        .filter(Habitacion.activa == True)
        .order_by(Habitacion.grupo, Habitacion.nombre)
        .all()
    )

    estancias_activas = (
        db.query(Estancia)
        .options(
            joinedload(Estancia.cliente),
            joinedload(Estancia.mascota)
        )
        .filter(
            Estancia.fecha_entrada <= fecha_consulta,
            Estancia.fecha_salida >= fecha_consulta
        )
        .all()
    )

    ocupacion_por_habitacion = {}

    for e in estancias_activas:
        if not e.habitacion:
            continue

        clave = normalizar_habitacion(e.habitacion)


        if clave not in ocupacion_por_habitacion:
            ocupacion_por_habitacion[clave] = []

        ocupacion_por_habitacion[clave].append(e)

    habitaciones_view = []

    for h in habitaciones:
        clave = normalizar_habitacion(h.nombre)
        estancias = ocupacion_por_habitacion.get(clave, [])

        estado = "libre"
        estancia = None
        conflicto = False

        if len(estancias) == 1:
            estancia = estancias[0]
            estado = "ocupada"

            if estancia.fecha_salida == fecha_consulta:
                estado = "sale_hoy"

            if estancia.fecha_entrada == fecha_consulta:
                estado = "entra_hoy"



        elif len(estancias) > 1:
            estancia = estancias[0]
            estado = "compartida"
            conflicto = False
        mascotas = [
            e.mascota.nombre
            for e in estancias
            if e.mascota
        ]
        habitaciones_view.append({
            "nombre": h.nombre,
            "grupo": h.grupo,
            "estado": estado,
            "conflicto": conflicto,
            "num_estancias": len(estancias),
            "estancia": estancia,
            "estancia_id": estancia.id if estancia else None,
            "mascotas": mascotas,
            "estancias":estancias
        })

    return templates.TemplateResponse(
        request=request,
        name="ocupacion/dashboard.html",
        context={
            "habitaciones": habitaciones_view,
            "hoy": fecha_consulta,

        }
    )

@router.get("/informes/ocupacion")
def informes_ocupacion(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="informes/ocupacion.html",
        context={}
    )

@router.get("/informes/ingresos")
def informes_ingresos(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="informes/ingresos.html",
        context={}
    )

@router.get("/api/ingresos-mensuales")
def api_ingresos_mensuales(db: Session = Depends(get_db)):

    hoy = date.today()

    datos = []

    for i in range(1, 13):

        inicio = date(hoy.year, i, 1)

        if i == 12:
            fin = date(hoy.year + 1, 1, 1)
        else:
            fin = date(hoy.year, i + 1, 1)

        facturas = db.query(Factura).filter(
            Factura.fecha >= inicio,
            Factura.fecha < fin
        ).all()

        total_mes = sum(f.total for f in facturas)

        datos.append({
            "mes": inicio.strftime("%b"),
            "total": float(total_mes)
        })

    return datos

@router.get("/informes/exportacion")
def informes_exportacion(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="informes/exportacion.html",
        context={}
    )
@router.get("/informes/clientes-consumo")
def informes_clientes_consumo(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="informes/clientes_consumo.html",
        context={}
    )
@router.get("/api/clientes-consumo")
def api_clientes_consumo(db: Session = Depends(get_db)):

    clientes = db.query(Cliente).all()

    resultado = []

    for c in clientes:

        estancias = (
            db.query(Estancia)
            .filter(Estancia.cliente_id == c.id)
            .all()
        )

        if not estancias:
            continue

        total_importe = 0

        for e in estancias:
            base = float(e.total or 0)
            extras = float(e.importe_extras or 0)
            camaras = float(e.importe_camaras or 0)
            transporte = float(e.importe_transporte or 0)
            veterinario = float(e.importe_veterinario or 0)

            total_importe += (
                    base +
                    extras +
                    camaras +
                    transporte +
                    veterinario
            )
        total_dias = sum(int(e.num_dias or 0) for e in estancias)

        total_extras = sum(float(e.importe_extras or 0) for e in estancias)
        total_camaras = sum(float(e.importe_camaras or 0) for e in estancias)
        total_transporte = sum(float(e.importe_transporte or 0) for e in estancias)
        total_veterinario = sum(float(e.importe_veterinario or 0) for e in estancias)

        visitas = len(estancias)

        resultado.append({
            "cliente": f"{c.nombre} {c.apellidos or ''}",
            "visitas": visitas,
            "dias": total_dias,
            "importe": round(total_importe, 2),
            "extras": round(total_extras, 2),
            "camaras": round(total_camaras, 2),
            "transporte": round(total_transporte, 2),
            "veterinario": round(total_veterinario, 2),
            "ticket_medio": round(total_importe / visitas, 2) if visitas else 0,
            "ultima_estancia": max(e.fecha_entrada for e in estancias).isoformat()
        })

    resultado.sort(key=lambda x: x["importe"], reverse=True)

    return resultado
@router.get("/informes/razas")
def informes_razas(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="informes/razas.html",
        context={}
    )
@router.get("/api/razas-estadisticas")
def api_razas_estadisticas(db: Session = Depends(get_db)):

    mascotas = db.query(Mascota).all()

    agrupadas = {}

    for m in mascotas:

        raza = m.raza or "Sin raza"

        if raza not in agrupadas:
            agrupadas[raza] = {
                "raza": raza,
                "tamano": m.tamano or "",
                "mascotas": 0,
                "estancias": 0,
                "dias": 0,
                "importe": 0,
                "camaras": 0,
                "transporte": 0,
                "veterinario": 0,
                "comp_personas": {},
                "comp_perros": {}
            }

        agrupadas[raza]["mascotas"] += 1
        cp = m.comportamiento_personas or "Sin dato"
        cd = m.comportamiento_perros or "Sin dato"

        agrupadas[raza]["comp_personas"][cp] = (
                agrupadas[raza]["comp_personas"].get(cp, 0) + 1
        )

        agrupadas[raza]["comp_perros"][cd] = (
                agrupadas[raza]["comp_perros"].get(cd, 0) + 1
        )



        estancias = (
            db.query(Estancia)
            .filter(Estancia.mascota_id == m.id)
            .all()
        )

        agrupadas[raza]["estancias"] += len(estancias)

        for e in estancias:

            agrupadas[raza]["dias"] += int(e.num_dias or 0)

            agrupadas[raza]["importe"] += (
                float(e.total or 0)
                + float(e.importe_extras or 0)
                + float(e.importe_camaras or 0)
                + float(e.importe_transporte or 0)
                + float(e.importe_veterinario or 0)
            )

            agrupadas[raza]["camaras"] += float(e.importe_camaras or 0)

            agrupadas[raza]["transporte"] += float(e.importe_transporte or 0)

            agrupadas[raza]["veterinario"] += float(e.importe_veterinario or 0)

    resultado = list(agrupadas.values())

    for r in resultado:
        r["comp_personas"] = ", ".join(
            f"{k}: {v}" for k, v in r["comp_personas"].items()
        )

        r["comp_perros"] = ", ".join(
            f"{k}: {v}" for k, v in r["comp_perros"].items()
        )

    resultado.sort(
        key=lambda x: x["importe"],
        reverse=True
    )

    return resultado

@router.get("/informes/comparativas")
def informes_comparativas(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="informes/comparativas.html",
        context={}
    )
@router.get("/api/comparativas-mensuales")
def api_comparativas_mensuales(
    db: Session = Depends(get_db)
):

    hoy = date.today()

    datos = []

    for i in range(1, 13):

        inicio = date(hoy.year, i, 1)

        if i == 12:
            fin = date(hoy.year + 1, 1, 1)
        else:
            fin = date(hoy.year, i + 1, 1)

        estancias = db.query(Estancia).filter(
            Estancia.fecha_entrada >= inicio,
            Estancia.fecha_entrada < fin
        ).all()

        clientes = set()

        ingresos = 0
        dias = 0

        for e in estancias:

            clientes.add(e.cliente_id)

            ingresos += (
                float(e.total or 0)
                + float(e.importe_extras or 0)
                + float(e.importe_camaras or 0)
                + float(e.importe_transporte or 0)
                + float(e.importe_veterinario or 0)
            )

            dias += int(e.num_dias or 0)

        ticket_medio = 0

        if estancias:
            ticket_medio = ingresos / len(estancias)

        datos.append({
            "mes": inicio.strftime("%b"),
            "ingresos": round(ingresos, 2),
            "estancias": len(estancias),
            "clientes": len(clientes),
            "dias": dias,
            "ticket_medio": round(ticket_medio, 2)
        })

    return datos

@router.get("/api/comparativas-anuales")
def api_comparativas_anuales(
    db: Session = Depends(get_db)
):

    años = {}

    estancias = db.query(Estancia).all()

    for e in estancias:

        if not e.fecha_entrada:
            continue

        año = e.fecha_entrada.year

        if año not in años:

            años[año] = {
                "año": año,
                "ingresos": 0,
                "estancias": 0,
                "clientes": set(),
                "dias": 0
            }

        años[año]["estancias"] += 1

        años[año]["clientes"].add(e.cliente_id)

        años[año]["dias"] += int(e.num_dias or 0)

        años[año]["ingresos"] += (
            float(e.total or 0)
            + float(e.importe_extras or 0)
            + float(e.importe_camaras or 0)
            + float(e.importe_transporte or 0)
            + float(e.importe_veterinario or 0)
        )

    resultado = []

    for año, datos in años.items():

        ticket_medio = 0

        if datos["estancias"] > 0:
            ticket_medio = (
                datos["ingresos"] /
                datos["estancias"]
            )

        resultado.append({
            "año": año,
            "ingresos": round(datos["ingresos"], 2),
            "estancias": datos["estancias"],
            "clientes": len(datos["clientes"]),
            "dias": datos["dias"],
            "ticket_medio": round(ticket_medio, 2)
        })

    resultado.sort(
        key=lambda x: x["año"]
    )

    return resultado
@router.get("/informes/comparativas-anuales")
def informes_comparativas_anuales(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="informes/comparativas_anuales.html",
        context={}
    )