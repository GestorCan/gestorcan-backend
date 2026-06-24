# app/routers/estancias.py
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.schemas.estancia import EstanciaCreate, EstanciaUpdate, EstanciaOut
from app.crud import estancias as crud_estancias
from fastapi import Request
from app.models.clientes import Cliente
from app.models.mascotas import Mascota
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import tempfile
from app.pdf.albaran_pdf import generar_pdf_albaran
import os
from sqlalchemy.orm import relationship
from app.models.estancia import Estancia
cliente = relationship("Cliente")
mascota = relationship("Mascota")
from sqlalchemy.orm import Session, joinedload
from app.services.tarifas_service import obtener_precio_tarifa
from app.database import get_db
from app.models.estancia import Estancia
from fastapi.responses import HTMLResponse, RedirectResponse
from io import BytesIO
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from decimal import Decimal
import os
import time
from app.models.factura import Factura
from app.pdf.factura_pdf import generar_pdf_factura
from app.services.factura_service import crear_factura_desde_estancia
from app.services.asignacion_habitaciones_service import sugerir_habitacion
from app.models.mascotas import Mascota
from app.schemas.estancia_asignacion import (AsignarHabitacionEstanciaRequest)
from app.services.asignacion_habitaciones_service import ( asignar_habitacion_estancia)
from app.models.tarifa_model import Tarifa
from decimal import Decimal
from typing import Optional
from typing import Optional
from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

emplates = Jinja2Templates(directory="app/templates")
precio = obtener_precio_tarifa("estancia_dia", "normal")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_PATH = os.path.join(BASE_DIR, "templates")
output_dir = os.path.join(BASE_DIR, "media", "albaranes")
templates = Jinja2Templates(directory=TEMPLATES_PATH)
router = APIRouter( prefix="/estancias", tags=["Estancias / Albaranes"])






from sqlalchemy import or_

@router.get("/listado", response_class=HTMLResponse)
def listado_estancias(
    request: Request,
    facturado: Optional[str] = None,
    buscar: Optional[str] = None,
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Estancia)
        .options(
            joinedload(Estancia.cliente),
            joinedload(Estancia.mascota),
        )
        .join(Estancia.cliente)
        .join(Estancia.mascota)
    )

    if facturado == "1":
        query = query.filter(Estancia.facturado == 1)
    elif facturado == "0":
        query = query.filter(Estancia.facturado == 0)

    if buscar:
        texto = f"%{buscar}%"
        query = query.filter(
            or_(
                Cliente.nombre.ilike(texto),
                Cliente.apellidos.ilike(texto),
                Cliente.dni.ilike(texto),
                Mascota.nombre.ilike(texto),
                Estancia.habitacion.ilike(texto),
            )
        )

    total = query.count()

    estancias = (
        query
        .order_by(Estancia.fecha_entrada.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="estancias_listado.html",
        context={
            "estancias": estancias,
            "facturado": facturado,
            "buscar": buscar or "",
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
        },
    )

@router.get("/exportar-excel")
def exportar_estancias_excel(db: Session = Depends(get_db)):
    estancias = (
        db.query(Estancia)
        .order_by(Estancia.fecha_entrada.desc())
        .all()
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Estancias"

    columnas = [
        "Albarán",
        "Entrada",
        "Salida",
        "Habitación",
        "Observaciones",
        "Precio Día",
        "Extras",
        "Cámaras",
        "Veterinario",
        "Transporte",
        "Total",
        "Pagado",
    ]

    ws.append(columnas)

    for estancia in estancias:
        ws.append([
            estancia.id,
            str(estancia.fecha_entrada or ""),
            str(estancia.fecha_salida or ""),
            estancia.habitacion or "",
            estancia.observaciones or "",
            estancia.precio_dia or 0,
            estancia.extras or "",
            estancia.camaras or 0,
            estancia.veterinario or 0,
            estancia.transporte or 0,
            estancia.total or 0,
            "Sí" if estancia.pagado else "No",
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=listado_estancias.xlsx"
        }
    )

@router.get("/form", response_class=HTMLResponse)
def formulario_estancia(
    request: Request,
    db: Session = Depends(get_db)
):
    clientes = db.query(Cliente).all()
    mascotas = db.query(Mascota).all()

    extras_tarifas = (
        db.query(Tarifa)
        .filter(
            Tarifa.concepto == "extra",
            Tarifa.activo == True
        )
        .order_by(Tarifa.tipo)
        .all()
    )

    tarifas_dia = (
        db.query(Tarifa)
        .filter(
            Tarifa.concepto == "estancia_dia",
            Tarifa.activo == True
        )
        .order_by(Tarifa.tipo)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "estancias_form.html",
        {
            "clientes": clientes,
            "mascotas": mascotas,
            "extras_tarifas": extras_tarifas,
            "tarifas_dia": tarifas_dia
        }
    )

@router.get("/", response_model=list[EstanciaOut])
def listar_estancias(db: Session = Depends(get_db)):
    return crud_estancias.obtener_estancias(db)

@router.get("/{estancia_id}/sugerir-habitacion")
def sugerir_habitacion_estancia(estancia_id: int, mascota_id: int, db: Session = Depends(get_db)):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()

    if not mascota:
        return {
            "ok": False,
            "mensaje": "Mascota no encontrada"
        }

    tamano = mascota.tamano.lower()

    residencia_id = 1  # provisional hasta tener multi-residencia completo

    sugerencia = sugerir_habitacion(
        db=db,
        residencia_id=residencia_id,
        tamano_mascota=tamano
    )

    return {
        "ok": True,
        "estancia_id": estancia_id,
        "mascota_id": mascota_id,
        "mascota": mascota.nombre,
        "tamano": tamano,
        "sugerencia": sugerencia
    }

@router.post("/{estancia_id}/asignar-habitacion")
def asignar_habitacion(estancia_id: int, datos: AsignarHabitacionEstanciaRequest, db: Session = Depends(get_db)):

    return asignar_habitacion_estancia(
        db=db,
        estancia_id=estancia_id,
        mascota_id=datos.mascota_id,
        fecha_entrada=datos.fecha_entrada,
        fecha_salida=datos.fecha_salida,
        confirmar_compartida=datos.confirmar_compartida
    )


@router.get("/{estancia_id}/factura-preview-pdf")
def factura_preview_pdf(estancia_id: int, db: Session = Depends(get_db)):
    estancia = (
        db.query(Estancia)
        .filter(Estancia.id == estancia_id)
        .first()
    )

    if not estancia:
        raise HTTPException(status_code=404)

    factura = (
        db.query(Factura)
        .filter(Factura.estancia_id == estancia.id)
        .first()
    )

    if not factura:
        factura = Factura(
            numero_factura=f"PREVIEW-{estancia.id}",
            estancia_id=estancia.id,
            base_imponible=0,
            iva=0,
            total=estancia.total or 0
        )

    pdf_path = generar_pdf_factura(
        factura,
        estancia,
        estancia.cliente,
        estancia.mascota,
        output_path=f"media/facturas_preview/preview_{estancia_id}.pdf"
    )

    return FileResponse(
        pdf_path,
        media_type="application/pdf"
    )

@router.post("/{estancia_id}/facturar-confirmar")
def facturar_confirmar( estancia_id: int, db: Session = Depends(get_db)):
    factura = crear_factura_desde_estancia(
        db=db,
        estancia_id=estancia_id
    )

    return RedirectResponse(
        url="/estancias/listado",
        status_code=303
    )

@router.get("/{estancia_id}/factura-preview")
def factura_preview(estancia_id: int, request: Request, db: Session = Depends(get_db)):
    estancia = (
        db.query(Estancia)
        .filter(Estancia.id == estancia_id)
        .first()
    )

    if not estancia:
        return RedirectResponse(
            url="/dashboard/estancias",
            status_code=303
        )

    cliente = (
        db.query(Cliente)
        .filter(Cliente.id == estancia.cliente_id)
        .first()
    )

    mascota = (
        db.query(Mascota)
        .filter(Mascota.id == estancia.mascota_id)
        .first()
    )

    total = estancia.total or Decimal("0")

    base = (total / Decimal("1.21")).quantize(Decimal("0.01"))
    iva = (total - base).quantize(Decimal("0.01"))
    total = total.quantize(Decimal("0.01"))

    return templates.TemplateResponse(
        request=request,
        name="facturas/preview.html",
        context={
            "estancia": estancia,
            "cliente": cliente,
            "mascota": mascota,
            "base": base,
            "iva": iva,
            "total": total,
        }
    )

@router.get("/{estancia_id}/pdf")
def pdf_estancia(estancia_id: int, db: Session = Depends(get_db)):

    estancia = (
        db.query(Estancia)
        .options(
            joinedload(Estancia.cliente),
            joinedload(Estancia.mascota)
        )
        .filter(Estancia.id == estancia_id)
        .first()
    )

    if not estancia:
        raise HTTPException(status_code=404, detail="Estancia no encontrada")

    output_dir = "media/albaranes"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(
        output_dir,
        f"albaran_{estancia_id}.pdf"
    )

    if not os.path.exists(output_path):
        generar_pdf_albaran(estancia, output_path)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=f"albaran_{estancia_id}.pdf"
    )

@router.get("/{estancia_id}/editar", response_class=HTMLResponse)
def editar_estancia_form(estancia_id: int,request: Request, db: Session = Depends(get_db)):

    estancia = db.query(Estancia).filter(Estancia.id == estancia_id).first()

    if not estancia:
        return RedirectResponse(url="/estancias/listado", status_code=303)

    clientes = db.query(Cliente).all()
    mascotas = db.query(Mascota).all()

    extras_tarifas = (
        db.query(Tarifa)
        .filter(
            Tarifa.concepto == "extra",
            Tarifa.activo == True
        )
        .order_by(Tarifa.tipo)
        .all()
    )
    tarifas_dia = (
        db.query(Tarifa)
        .filter(
            Tarifa.concepto == "estancia_dia",
            Tarifa.activo == True
        )
        .order_by(Tarifa.tipo)
        .all()
    )

    return templates.TemplateResponse(
        name="estancias_form.html",
        request=request,
        context={
            "estancia": estancia,
            "modo": "editar",
            "clientes": clientes,
            "mascotas": mascotas,
            "extras_tarifas": extras_tarifas,
            "tarifas_dia": tarifas_dia,
        }
    )

@router.get("/{estancia_id}", response_model=EstanciaOut)
def detalle_estancia(estancia_id: int, db: Session = Depends(get_db)):

    estancia = crud_estancias.obtener_estancia(db, estancia_id)

    if not estancia:
        raise HTTPException(status_code=404, detail="Estancia no encontrada")

    return estancia


@router.put("/{estancia_id}", response_model=EstanciaOut)
def editar_estancia(estancia_id: int, datos: EstanciaUpdate, db: Session = Depends(get_db)):

    if datos.fecha_entrada > datos.fecha_salida:
        raise HTTPException(
            status_code=400,
            detail="La fecha de entrada no puede ser posterior a la salida"
        )

    estancia_actual = crud_estancias.obtener_estancia(db, estancia_id)

    if not estancia_actual:
        raise HTTPException(
            status_code=404,
            detail="Estancia no encontrada"
        )

    if estancia_actual.facturado:
        raise HTTPException(
            status_code=400,
            detail="ALBARÁN FACTURADO. No se puede modificar."
        )

    estancia = crud_estancias.actualizar_estancia(db, estancia_id, datos)

    return estancia

@router.delete("/{estancia_id}")
def eliminar_estancia(estancia_id: int, db: Session = Depends(get_db)):

    estancia = crud_estancias.borrar_estancia(db, estancia_id)

    if not estancia:
        raise HTTPException(status_code=404, detail="Estancia no encontrada")

    return {"mensaje": "Estancia eliminada correctamente"}

@router.post("/", response_model=EstanciaOut)
def crear_estancia( estancia: EstanciaCreate, db: Session = Depends(get_db)):

    if estancia.fecha_entrada > estancia.fecha_salida:
        raise HTTPException(
            status_code=400,
            detail="La fecha de entrada no puede ser posterior a la salida"
        )

    return crud_estancias.crear_estancia(db, estancia)


@router.post("/{estancia_id}/marcar-pagado-listado")
def marcar_pagado_desde_listado( estancia_id: int, db: Session = Depends(get_db)):

    estancia = db.query(Estancia).filter(Estancia.id == estancia_id).first()

    if estancia:
        estancia.pagado = True
        db.commit()

    return RedirectResponse(
        url="/estancias/listado",
        status_code=303
    )


@router.put("/{estancia_id}/marcar-pagado")
def marcar_estancia_pagada(estancia_id: int, db: Session = Depends(get_db)):

    estancia = db.query(Estancia).filter(Estancia.id == estancia_id).first()

    if not estancia:
        raise HTTPException(status_code=404, detail="Estancia no encontrada")

    estancia.pagado = True

    db.commit()
    db.refresh(estancia)

    return {
        "mensaje": "Estancia marcada como pagada",
        "id": estancia.id,
        "pagado": estancia.pagado,
        "total": estancia.total
    }

@router.post("/{estancia_id}/facturar")
def marcar_facturado( estancia_id: int, db: Session = Depends(get_db)):

    estancia = (
        db.query(Estancia)
        .filter(Estancia.id == estancia_id)
        .first()
    )

    if estancia:
        estancia.facturado = True
        db.commit()

    return RedirectResponse(
        url="/estancias/listado",
        status_code=303
    )
@router.post("/{estancia_id}/editar")
def editar_estancia(estancia_id: int,data: EstanciaCreate, db: Session = Depends(get_db)):

    estancia = (
        db.query(Estancia)
        .filter(Estancia.id == estancia_id)
        .first()
    )

    if not estancia:
        raise HTTPException(
            status_code=404,
            detail="Estancia no encontrada"
        )
    if estancia.facturado:
        raise HTTPException(
            status_code=403,
            detail="No se puede modificar una estancia ya facturada."
        )

    estancia.cliente_id = data.cliente_id
    estancia.mascota_id = data.mascota_id

    estancia.fecha_entrada = data.fecha_entrada
    estancia.hora_entrada = data.hora_entrada

    estancia.fecha_salida = data.fecha_salida
    estancia.hora_salida = data.hora_salida

    estancia.habitacion = data.habitacion

    estancia.tipo_precio_dia = data.tipo_precio_dia
    estancia.precio_dia = data.precio_dia



    estancia.num_dias = data.num_dias
    estancia.subtotal = data.num_dias * data.precio_dia

    estancia.extras = data.extras
    estancia.importe_extras = data.importe_extras

    estancia.camaras = data.camaras
    estancia.importe_camaras = data.importe_camaras

    estancia.transporte = data.transporte
    estancia.importe_transporte = data.importe_transporte

    estancia.veterinario = data.veterinario
    estancia.importe_veterinario = data.importe_veterinario

    estancia.pienso = data.pienso
    estancia.importe_pienso = data.importe_pienso

    estancia.num_dias = data.num_dias

    estancia.subtotal = (
            data.num_dias * data.precio_dia
    )

    estancia.total = (
            estancia.subtotal
            + data.importe_extras
            + data.importe_camaras
            + data.importe_veterinario
            + data.importe_pienso
            + data.importe_transporte
    )

    estancia.pagado = data.pagado
    estancia.observaciones = data.observaciones

    db.commit()
    db.refresh(estancia)

    return {
        "ok": True,
        "id": estancia.id
    }

