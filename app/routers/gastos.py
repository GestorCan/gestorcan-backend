from fastapi import APIRouter, Request, Depends,Form, UploadFile, File,Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.gasto import Gasto
from app.models.tipo_gasto import TipoGasto
from app.models.proveedor import Proveedor
from fastapi.responses import FileResponse
from typing import Optional
from fastapi.responses import RedirectResponse,StreamingResponse
from datetime import date
from pathlib import Path
import shutil
import json
from io import BytesIO
import pandas as pd
from sqlalchemy import Boolean, Integer, Date




router = APIRouter(
    prefix="/gastos",
    tags=["Gastos"]
)



templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = Path("static/uploads/gastos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
INFORMES_GASTOS_EXCEL_DIR = Path("static/informes/gastos/excel")
INFORMES_GASTOS_EXCEL_DIR.mkdir(parents=True, exist_ok=True)




@router.get("")
def gastos_home(
    request: Request,
    db: Session = Depends(get_db)
):
    total_gastos = db.query(Gasto).count()

    total_tickets = (
        db.query(Gasto)
        .filter(Gasto.tipo_documento == "ticket")
        .count()
    )

    total_facturas = (
        db.query(Gasto)
        .filter(Gasto.tipo_documento == "factura")
        .count()
    )

    return templates.TemplateResponse(
        request=request,
        name="gastos/dashboard.html",
        context={
            "total_gastos": total_gastos,
            "total_tickets": total_tickets,
            "total_facturas": total_facturas,
        }
    )
@router.get("/nuevo")
def nuevo_gasto(
    request: Request,
    db: Session = Depends(get_db)
):
    proveedores = (
        db.query(Proveedor)
        .order_by(Proveedor.nombre)
        .all()
    )

    tipos_gasto = (
        db.query(TipoGasto)
        .order_by(TipoGasto.nombre)
        .all()
    )
    proveedores_json = [
        {
            "nombre": p.nombre,
            "tipo_gasto": p.tipo_gasto_defecto or "",
            "retencion": p.porcentaje_retencion_defecto or 0
        }
        for p in proveedores
    ]
    return templates.TemplateResponse(
        request=request,
        name="gastos/nuevo.html",
        context={
            "proveedores": proveedores,
            "tipos_gasto": tipos_gasto,
            "proveedores_json": json.dumps(proveedores_json)
        }
    )

@router.post("/nuevo")
def guardar_gasto(
    tipo_documento: str = Form(...),
    fecha: date = Form(...),
    proveedor: str = Form(...),
    tipo_gasto: str = Form(...),
    importe: float = Form(0),

    numero_factura: str = Form(None),
    concepto: str = Form(None),
    base_imponible: float = Form(0),
    porcentaje_iva: float = Form(0),
    importe_iva: float = Form(0),
    porcentaje_retencion: float = Form(0),
    importe_retencion: float = Form(0),
    total_factura: float = Form(0),

    archivo: UploadFile = File(None),

    db: Session = Depends(get_db)
):
    archivo_path = None

    if archivo and archivo.filename:
        ruta_archivo = UPLOAD_DIR / archivo.filename

        with ruta_archivo.open("wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)

        archivo_path = f"/static/uploads/gastos/{archivo.filename}"

    if tipo_documento == "ticket":
        total_factura = importe
        base_imponible = 0
        porcentaje_iva = 0
        importe_iva = 0
        porcentaje_retencion = 0
        importe_retencion = 0
        numero_factura = None
        concepto = None

    gasto = Gasto(
        tipo_documento=tipo_documento,
        fecha=fecha,
        proveedor=proveedor.strip(),
        tipo_gasto=tipo_gasto.strip(),
        importe=importe,
        numero_factura=numero_factura,
        concepto=concepto,
        base_imponible=base_imponible,
        porcentaje_iva=porcentaje_iva,
        importe_iva=importe_iva,
        porcentaje_retencion=porcentaje_retencion,
        importe_retencion=importe_retencion,
        total_factura=total_factura,
        archivo_path=archivo_path,
    )

    db.add(gasto)
    db.commit()

    return RedirectResponse(
        url="/gastos/listado",
        status_code=303
    )




@router.get("/listado")
def gastos_listado(
    request: Request,
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    proveedor: Optional[str] = Query(None),
    tipo_gasto: Optional[str] = Query(None),
    tipo_documento: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Gasto)

    if fecha_desde:
        query = query.filter(Gasto.fecha >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Gasto.fecha <= fecha_hasta)

    if proveedor:
        query = query.filter(Gasto.proveedor == proveedor)

    if tipo_gasto:
        query = query.filter(Gasto.tipo_gasto == tipo_gasto)

    if tipo_documento:
        query = query.filter(Gasto.tipo_documento == tipo_documento)

    gastos = (
        query
        .order_by(Gasto.fecha.desc(), Gasto.id.desc())
        .all()
    )

    proveedores = (
        db.query(Proveedor)
        .order_by(Proveedor.nombre)
        .all()
    )

    tipos_gasto = (
        db.query(TipoGasto)
        .order_by(TipoGasto.nombre)
        .all()
    )

    total_gastos = sum(
        float(g.total_factura or g.importe or 0)
        for g in gastos
    )

    iva_soportado = sum(
        float(g.importe_iva or 0)
        for g in gastos
        if (g.tipo_documento or "").lower() == "factura"
    )

    total_facturas = sum(
        1 for g in gastos
        if (g.tipo_documento or "").lower() == "factura"
    )

    total_tickets = sum(
        1 for g in gastos
        if (g.tipo_documento or "").lower() == "ticket"
    )

    return templates.TemplateResponse(
        request=request,
        name="gastos/listado.html",
        context={
            "gastos": gastos,
            "proveedores": proveedores,
            "tipos_gasto": tipos_gasto,

            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "proveedor_filtro": proveedor,
            "tipo_gasto_filtro": tipo_gasto,
            "tipo_documento_filtro": tipo_documento,

            "total_gastos": total_gastos,
            "iva_soportado": iva_soportado,
            "total_facturas": total_facturas,
            "total_tickets": total_tickets,
        }
    )
@router.post("/borrar/{gasto_id}")
def borrar_gasto(
    gasto_id: int,
    db: Session = Depends(get_db)
):
    gasto = db.query(Gasto).get(gasto_id)

    if gasto:
        db.delete(gasto)
        db.commit()

    return RedirectResponse(
        url="/gastos/listado",
        status_code=303
    )
@router.get("/editar/{gasto_id}")
def editar_gasto(
    gasto_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    gasto = (
        db.query(Gasto)
        .filter(Gasto.id == gasto_id)
        .first()
    )

    proveedores = (
        db.query(Proveedor)
        .order_by(Proveedor.nombre)
        .all()
    )

    tipos_gasto = (
        db.query(TipoGasto)
        .order_by(TipoGasto.nombre)
        .all()
    )

    if not gasto:
        return RedirectResponse(
            url="/gastos/listado",
            status_code=303
        )
    proveedores_json = [
        {
            "nombre": p.nombre,
            "tipo_gasto": p.tipo_gasto_defecto or "",
            "retencion": p.porcentaje_retencion_defecto or 0
        }
        for p in proveedores
    ]

    return templates.TemplateResponse(
        request=request,
        name="gastos/editar.html",
        context={
            "gasto": gasto,
            "proveedores": proveedores,
            "tipos_gasto": tipos_gasto,
            "proveedores_json": json.dumps(proveedores_json)
        }
    )
@router.post("/editar/{gasto_id}")
def guardar_edicion_gasto(
    gasto_id: int,
    tipo_documento: str = Form(...),
    fecha: date = Form(...),
    proveedor: str = Form(...),
    tipo_gasto: str = Form(...),
    importe: float = Form(0),
    numero_factura: str = Form(None),
    concepto: str = Form(None),
    base_imponible: float = Form(0),
    porcentaje_iva: float = Form(0),
    importe_iva: float = Form(0),
    porcentaje_retencion: float = Form(0),
    importe_retencion: float = Form(0),
    total_factura: float = Form(0),
    archivo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    gasto = (
        db.query(Gasto)
        .filter(Gasto.id == gasto_id)
        .first()
    )

    if not gasto:
        return RedirectResponse(
            url="/gastos/listado",
            status_code=303
        )

    if archivo and archivo.filename:
        ruta_archivo = UPLOAD_DIR / archivo.filename

        with ruta_archivo.open("wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)

        gasto.archivo_path = f"/static/uploads/gastos/{archivo.filename}"

    if tipo_documento == "ticket":
        total_factura = importe
        base_imponible = 0
        porcentaje_iva = 0
        importe_iva = 0
        porcentaje_retencion = 0
        importe_retencion = 0
        numero_factura = None
        concepto = None

    gasto.tipo_documento = tipo_documento
    gasto.fecha = fecha
    gasto.proveedor = proveedor.strip()
    gasto.tipo_gasto = tipo_gasto.strip()
    gasto.importe = importe

    gasto.numero_factura = numero_factura
    gasto.concepto = concepto

    gasto.base_imponible = base_imponible
    gasto.porcentaje_iva = porcentaje_iva
    gasto.importe_iva = importe_iva
    gasto.porcentaje_retencion = porcentaje_retencion
    gasto.importe_retencion = importe_retencion
    gasto.total_factura = total_factura

    db.commit()

    return RedirectResponse(
        url="/gastos/listado",
        status_code=303
    )
@router.get("/exportar_excel")
def exportar_excel(
    db: Session = Depends(get_db)
):

    gastos = (
        db.query(Gasto)
        .order_by(Gasto.fecha.desc())
        .all()
    )

    datos = []

    for gasto in gastos:
        datos.append({
            "Fecha": gasto.fecha,
            "Proveedor": gasto.proveedor,
            "Tipo gasto": gasto.tipo_gasto,
            "Total": gasto.total_factura,
        })

    df = pd.DataFrame(datos)

    # AQUÍ
    nombre_archivo = datetime.now().strftime(
        "gastos_%Y-%m-%d_%H-%M.xlsx"
    )

    ruta_excel = INFORMES_GASTOS_EXCEL_DIR / nombre_archivo

    # Guardar Excel
    with pd.ExcelWriter(
        ruta_excel,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Gastos"
        )

    return FileResponse(
        path=ruta_excel,
        filename=nombre_archivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )