from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.verifactu_registro import VeriFactuRegistro
from app.models.factura import Factura
from fastapi import Form
from app.services.factura_service import (
    crear_factura_rectificativa
)
from fastapi.responses import RedirectResponse
router = APIRouter()
from fastapi import HTTPException
templates = Jinja2Templates(directory="app/templates")


def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("")
def dashboard_verifactu(request: Request,db: Session = Depends(get_db)):

    registros = (
        db.query(VeriFactuRegistro)
        .order_by(
            VeriFactuRegistro.id.desc()
        )
        .all()
    )

    total = len(registros)

    pendientes = len([
        r for r in registros
        if r.estado == "pendiente"
    ])

    firmados = len([
        r for r in registros
        if r.signed_xml_path
    ])

    enviados = len([
        r for r in registros
        if r.enviado
    ])

    errores = len([
        r for r in registros
        if r.estado == "error"
    ])

    facturas = (
        db.query(Factura)
        .order_by(Factura.fecha.desc())
        .all()
    )

    rectificativas = (
        db.query(VeriFactuRegistro)
        .filter(
            VeriFactuRegistro.tipo_factura == "rectificativa"
        )
        .count()
    )




    print("FIRMADOS:", firmados)

    return templates.TemplateResponse(
        request=request,
        name="fiscal/verifactu/dashboard.html",

        context={
            "registros": registros,
            "total": total,
            "pendientes": pendientes,
            "firmados": firmados,
            "enviados": enviados,
            "errores": errores,
            "facturas": facturas,
            "rectificativas": rectificativas
        }
    )
@router.get("/facturas/{factura_id}/rectificar")
def formulario_rectificativa(
    factura_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    factura = (
        db.query(Factura)
        .filter(Factura.id == factura_id)
        .first()
    )

    if not factura:
        raise HTTPException(
            status_code=404,
            detail="Factura no encontrada"
        )
    estancia = factura.estancia

    conceptos = []

    if estancia:
        alojamiento = (
                float(estancia.precio_dia or 0)
                * int(estancia.num_dias or 0)
        )

        conceptos = [
            {
                "nombre": "Alojamiento",
                "importe": alojamiento
            },
            {
                "nombre": "Extras",
                "importe": float(estancia.importe_extras or 0)
            },
            {
                "nombre": "Cámaras",
                "importe": float(estancia.importe_camaras or 0)
            },
            {
                "nombre": "Transporte",
                "importe": float(estancia.importe_transporte or 0)
            },
            {
                "nombre": "Veterinario",
                "importe": float(estancia.importe_veterinario or 0)
            }
        ]
    return templates.TemplateResponse(
        request=request,
        name="fiscal/verifactu/rectificativa_form.html",
        context={
            "factura": factura,
            "conceptos": conceptos
        }
    )
@router.post("/facturas/{factura_id}/rectificar")
def crear_rectificativa(
    factura_id: int,
    motivo: str = Form(...),
    total_rectificado: float = Form(...),
    db: Session = Depends(get_db)
):

    factura = crear_factura_rectificativa(
        db=db,
        factura_original_id=factura_id,
        motivo=motivo,
        total_rectificado=total_rectificado
    )

    return RedirectResponse(
        url="/fiscal/verifactu",
        status_code=303
    )

from fastapi.responses import FileResponse

@router.get("/descargar-pdf/{factura_id}")
def descargar_pdf(
    factura_id: int,
    db: Session = Depends(get_db)
):
    factura = db.query(Factura).get(factura_id)

    return FileResponse(
        factura.pdf_path,
        filename=factura.numero_factura + ".pdf"
    )
from fastapi.responses import FileResponse

@router.get("/facturas/{factura_id}/pdf")
def descargar_pdf(
    factura_id: int,
    db: Session = Depends(get_db)
):

    factura = (
        db.query(Factura)
        .filter(Factura.id == factura_id)
        .first()
    )

    if not factura:
        raise HTTPException(
            status_code=404,
            detail="Factura no encontrada"
        )

    return FileResponse(
        factura.pdf_path,
        filename=f"{factura.numero_factura}.pdf"
    )