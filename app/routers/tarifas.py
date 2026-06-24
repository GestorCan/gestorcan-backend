from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal
from app.models.tarifa_model import Tarifa
import os
from app.services.tarifas_service import obtener_precio_tarifa
from sqlalchemy import func
router = APIRouter(prefix="/tarifas", tags=["Tarifas"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))





@router.get("/api/precio")
def obtener_precio_api(concepto: str, tipo: str):
    db = SessionLocal()

    try:
        tarifa = (
            db.query(Tarifa)
            .filter(
                func.lower(Tarifa.concepto) == concepto.lower(),
                func.lower(Tarifa.tipo) == tipo.lower(),
                Tarifa.activo == True
            )
            .first()
        )

        if not tarifa:
            return {
                "precio": 0,
                "unidad": "unidad"
            }

        return {
            "precio": tarifa.precio or 0,
            "unidad": tarifa.unidad or "unidad"
        }

    finally:
        db.close()


# 🔹 PANEL
@router.get("/panel", response_class=HTMLResponse)
def panel_tarifas(request: Request):
    db = SessionLocal()

    try:
        tarifas_dia = (
            db.query(Tarifa)
            .filter(
                Tarifa.activo == True,
                Tarifa.concepto == "estancia_dia"
            )
            .order_by(Tarifa.tipo)
            .all()
        )

        servicios = (
            db.query(Tarifa)
            .filter(
                Tarifa.activo == True,
                Tarifa.concepto == "servicio"
            )
            .order_by(Tarifa.tipo)
            .all()
        )

        extras = (
            db.query(Tarifa)
            .filter(
                Tarifa.activo == True,
                Tarifa.concepto == "extra"
            )
            .order_by(Tarifa.tipo)
            .all()
        )

        return templates.TemplateResponse(
            request,
            "tarifas_panel.html",
            {
                "tarifas_dia": tarifas_dia,
                "servicios": servicios,
                "extras": extras
            }
        )

    finally:
        db.close()


# 🔹 ACTUALIZAR PRECIO
@router.post("/{tarifa_id}/actualizar")
def actualizar_tarifa(tarifa_id: int, precio: float = Form(...)):
    db = SessionLocal()
    try:
        tarifa = db.query(Tarifa).filter(Tarifa.id == tarifa_id).first()
        if tarifa:
            tarifa.precio = precio
            db.commit()

        return RedirectResponse("/tarifas/panel", status_code=303)
    finally:
        db.close()


@router.post("/{tarifa_id}/borrar")
def borrar_tarifa(tarifa_id: int):
    db = SessionLocal()
    try:
        tarifa = db.query(Tarifa).filter(Tarifa.id == tarifa_id).first()

        if tarifa:
            tarifa.activo = False
            db.commit()

        return RedirectResponse("/tarifas/panel", status_code=303)

    finally:
        db.close()




# 🔹 NUEVO EXTRA/SERVICIO
@router.post("/nueva")
def nueva_tarifa(
    concepto: str = Form(...),
    tipo: str = Form(...),
    precio: float = Form(...)
):
    db = SessionLocal()

    try:

        concepto_normalizado = (concepto or "").strip().lower()
        tipo_normalizado = (tipo or "").strip().lower()

        unidad = "unidad"

        if concepto_normalizado == "estancia_dia":
            unidad = "dia"

        elif concepto_normalizado == "servicio":

            if tipo_normalizado == "transporte":
                unidad = "km"
            else:
                unidad = "dia"

        nueva = Tarifa(
            concepto=concepto,
            tipo=tipo,
            precio=precio,
            unidad=unidad,
            activo=True
        )

        db.add(nueva)
        db.commit()

        return RedirectResponse(
            "/tarifas/panel",
            status_code=303
        )

    finally:
        db.close()

@router.get("/{tarifa_id}/eliminar")
def eliminar_tarifa(
    tarifa_id: int
):
    db = SessionLocal()

    try:

        tarifa = (
            db.query(Tarifa)
            .filter(Tarifa.id == tarifa_id)
            .first()
        )

        if tarifa:

            tarifa.activo = False

            db.commit()

        return RedirectResponse(
            "/tarifas/panel",
            status_code=303
        )

    finally:
        db.close()