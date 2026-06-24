from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.factura_service import crear_factura_desde_estancia
from app.services.factura_service import (
    crear_factura_desde_estancia,
    listar_facturas_con_verifactu,
    obtener_detalle_factura)
from fastapi.responses import FileResponse
from app.repositories.factura_repository import obtener_factura_por_id
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.models.factura import Factura
from app.services.factura_service import (crear_factura_rectificativa)
from pathlib import Path
from fastapi import HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi import Form
from fastapi import Request
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(
    prefix="/facturas",
    tags=["Facturas"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/{factura_id}/rectificar")
def formulario_rectificativa(
    request: Request,
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

    return templates.TemplateResponse(
        request=request,
        name="fiscal/verifactu/rectificativa_form.html",
        context={
            "factura": factura,
            "conceptos": []
        }
    )




@router.post("/{factura_id}/rectificar")
def rectificar_factura(
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
        url="/fiscal/libros-registro",
        status_code=303
    )





@router.post("/generar/{estancia_id}")
def generar_factura(estancia_id: int, db: Session = Depends(get_db)):
    try:
        factura = crear_factura_desde_estancia(db, estancia_id)

        return {
            "ok": True,
            "mensaje": "Factura generada correctamente",
            "factura_id": factura.id,
            "numero_factura": factura.numero_factura,
            "serie": factura.serie,
            "total": float(factura.total),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def listar_facturas(db: Session = Depends(get_db)):
    return listar_facturas_con_verifactu(db)


@router.get("/{factura_id}")
def detalle_factura(factura_id: int, db: Session = Depends(get_db)):
    try:
        return obtener_detalle_factura(db, factura_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.get("/{factura_id}/pdf")
def descargar_pdf_factura(factura_id: int, db: Session = Depends(get_db)):

    factura = obtener_factura_por_id(db, factura_id)

    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    BASE_DIR = Path(__file__).resolve().parents[2]

    ruta_pdf = None

    # 1. Si la factura tiene pdf_path, intentamos usarlo
    if factura.pdf_path:
        ruta_pdf = Path(factura.pdf_path)

        if not ruta_pdf.is_absolute():
            ruta_pdf = BASE_DIR / ruta_pdf

    # 2. Si no tiene pdf_path, buscamos por año y número
    else:
        if not factura.fecha:
            raise HTTPException(
                status_code=404,
                detail="La factura no tiene fecha para localizar el PDF"
            )

        anio = factura.fecha.year

        ruta_pdf = (
            BASE_DIR
            / "media"
            / "facturas"
            / str(anio)
            / f"{factura.numero_factura}.pdf"
        )

    if not ruta_pdf.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Archivo PDF no encontrado: {ruta_pdf}"
        )

    return FileResponse(
        str(ruta_pdf),
        media_type="application/pdf",
        filename=ruta_pdf.name
    )
@router.get("/estancia/{estancia_id}/pdf")
def factura_pdf_por_estancia(
    estancia_id: int,
    db: Session = Depends(get_db)
):
    factura = (
        db.query(Factura)
        .filter(Factura.estancia_id == estancia_id)
        .first()
    )

    if not factura:
        raise HTTPException(
            status_code=404,
            detail="Factura no encontrada para esta estancia"
        )

    return RedirectResponse(
        url=f"/facturas/{factura.id}/pdf",
        status_code=303
    )