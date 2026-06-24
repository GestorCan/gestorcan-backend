from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tipo_gasto import TipoGasto
from app.models.gasto import Gasto
from fastapi import APIRouter, Request, Depends, Form


router = APIRouter(
    prefix="/gastos/tipos",
    tags=["Tipos de gasto"]
)




templates = Jinja2Templates(directory="app/templates")


@router.get("")
def listado_tipos_gasto(
    request: Request,
    db: Session = Depends(get_db)
):
    tipos = (
        db.query(TipoGasto)
        .order_by(TipoGasto.nombre.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="gastos/tipos_gasto/listado.html",
        context={
            "tipos": tipos
        }
    )


@router.get("/nuevo")
def nuevo_tipo_gasto(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="gastos/tipos_gasto/nuevo.html",
        context={}
    )


@router.post("/nuevo")
def guardar_tipo_gasto(
    nombre: str = Form(...),
    iva_defecto: float = Form(21),
    db: Session = Depends(get_db)
):
    nombre = nombre.strip()

    existente = (
        db.query(TipoGasto)
        .filter(TipoGasto.nombre == nombre)
        .first()
    )

    if not existente:
        tipo = TipoGasto(
            nombre=nombre,
            iva_defecto=iva_defecto
        )
        db.add(tipo)
        db.commit()

    return RedirectResponse(
        url="/gastos/tipos",
        status_code=303
    )
@router.get("/editar/{tipo_id}")
def editar_tipo_gasto(
    tipo_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    tipo = (
        db.query(TipoGasto)
        .filter(TipoGasto.id == tipo_id)
        .first()
    )

    return templates.TemplateResponse(
        request=request,
        name="gastos/tipos_gasto/editar.html",
        context={
            "tipo": tipo
        }
    )
@router.post("/editar/{tipo_id}")
def guardar_edicion_tipo_gasto(
    tipo_id: int,
    nombre: str = Form(...),
    iva_defecto: float = Form(21),
    db: Session = Depends(get_db)
):
    tipo = (
        db.query(TipoGasto)
        .filter(TipoGasto.id == tipo_id)
        .first()
    )

    tipo.nombre = nombre.strip()
    tipo.iva_defecto = iva_defecto

    db.commit()

    return RedirectResponse(
        url="/gastos/tipos",
        status_code=303
    )
@router.post("/borrar/{tipo_id}")
def borrar_tipo_gasto(
    tipo_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    tipo = (
        db.query(TipoGasto)
        .filter(TipoGasto.id == tipo_id)
        .first()
    )

    tipos = (
        db.query(TipoGasto)
        .order_by(TipoGasto.nombre)
        .all()
    )

    if not tipo:
        return templates.TemplateResponse(
            request=request,
            name="gastos/tipos_gasto/listado.html",
            context={
                "tipos": tipos,
                "error": "Tipo de gasto no encontrado."
            }
        )

    gastos_asociados = (
        db.query(Gasto)
        .filter(Gasto.tipo_gasto == tipo.nombre)
        .count()
    )

    if gastos_asociados > 0:
        return templates.TemplateResponse(
            request=request,
            name="gastos/tipos_gasto/listado.html",
            context={
                "tipos": tipos,
                "error": (
                    f'No se puede borrar "{tipo.nombre}". '
                    f'Existen {gastos_asociados} gastos asociados.'
                )
            }
        )

    db.delete(tipo)
    db.commit()

    return RedirectResponse(
        url="/gastos/tipos",
        status_code=303
    )