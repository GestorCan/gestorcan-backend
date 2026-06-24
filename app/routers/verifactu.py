from fastapi import APIRouter, Depends

from app.database import get_db

from app.verifactu.dashboard_service import (
    obtener_dashboard_verifactu
)
from fastapi import Request
from fastapi.templating import Jinja2Templates
from app.models.factura import Factura
from fastapi.responses import FileResponse,RedirectResponse
import os

from app.verifactu.auditoria_pdf import generar_pdf_auditoria_verifactu

router = APIRouter()




from fastapi import Request
from fastapi.templating import Jinja2Templates
from app.models.verifactu_registro import VeriFactuRegistro
from app.verifactu.auditoria_service import verificar_cadena_hash
from sqlalchemy.orm import Session

from app.verifactu.auditoria_service import (
    verificar_cadena_hash,
    recalcular_cadena_hash
)

from fastapi.responses import FileResponse, RedirectResponse

from app.verifactu.envio_service import procesar_registros_pendientes



templates = Jinja2Templates(directory="app/templates")

@router.post("/enviar-pendientes")
def enviar_pendientes_verifactu(
    db: Session = Depends(get_db)
):
    resultado = procesar_registros_pendientes(db)

    return RedirectResponse(
        url=(
            "/fiscal/verifactu/"
            f"?msg=Envío simulado: "
            f"{resultado['enviados']} enviados, "
            f"{resultado['errores']} errores"
        ),
        status_code=303
    )




@router.get("/auditoria/pdf")
def descargar_pdf_auditoria(db: Session = Depends(get_db)):
    ruta_pdf = generar_pdf_auditoria_verifactu(db)

    return FileResponse(
        ruta_pdf,
        media_type="application/pdf",
        filename=os.path.basename(ruta_pdf)
    )




@router.get("/auditoria/verificar")
def verificar_hash_verifactu(db: Session = Depends(get_db)):
    return verificar_cadena_hash(db)

@router.post("/auditoria/recalcular-hash")
def recalcular_hash_verifactu(db: Session = Depends(get_db)):
    resultado = recalcular_cadena_hash(db)

    return RedirectResponse(
        url=f"/fiscal/verifactu/?msg=Cadena recalculada: {resultado['facturas_actualizadas']} facturas",
        status_code=303
    )
@router.get("/")
def verifactu_home(
    request: Request,
    db=Depends(get_db)
):
    datos = obtener_dashboard_verifactu(db)

    registros = (
        db.query(VeriFactuRegistro)
        .order_by(VeriFactuRegistro.id.desc())
        .all()
    )
    pendientes = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.enviado == False)
        .count()
    )
    auditoria = verificar_cadena_hash(db)
    facturas = (
        db.query(Factura)
        .order_by(Factura.fecha.asc(), Factura.id.asc())
        .all()
    )
    return templates.TemplateResponse(
        request=request,
        name="fiscal/verifactu/dashboard.html",
        context={
            "total_registros": datos["total"],
            "firmados": datos["firmados"],
            "aceptados": datos["aceptados"],
            "errores": datos["errores"],
            "pendientes": pendientes,
            "registros": registros,
            "auditoria": auditoria,
            "facturas": facturas,
        }
    )

@router.get("/dashboard")
def dashboard_verifactu(
    db=Depends(get_db)
):
    return obtener_dashboard_verifactu(db)