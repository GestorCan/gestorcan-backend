from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.database import get_db
from app.models.proveedor import Proveedor
from app.models.tipo_gasto import TipoGasto
from app.models.gasto import Gasto



router = APIRouter(
    prefix="/gastos/proveedores",
    tags=["Proveedores"]
)

templates = Jinja2Templates(
    directory="app/templates"
)

@router.get("/nuevo")
def nuevo_proveedor(
    request: Request,
    db: Session = Depends(get_db)
):

    tipos_gasto = (
        db.query(TipoGasto)
        .order_by(TipoGasto.nombre)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="gastos/proveedores/nuevo.html",
        context={
            "tipos_gasto": tipos_gasto
        }
    )
@router.post("/nuevo")
def guardar_proveedor(
    nombre: str = Form(...),
    cif: str = Form(None),
    telefono: str = Form(None),
    email: str = Form(None),
    tipo_gasto_defecto: str = Form(None),

    tiene_retencion: str = Form("no"),
    porcentaje_retencion_defecto: float = Form(0),

    db: Session = Depends(get_db)
):
    tipo_gasto_defecto = (
        tipo_gasto_defecto.strip()
        if tipo_gasto_defecto
        else None
    )

    if tipo_gasto_defecto:
        tipo_existente = (
            db.query(TipoGasto)
            .filter(TipoGasto.nombre == tipo_gasto_defecto)
            .first()
        )

        if not tipo_existente:
            nuevo_tipo = TipoGasto(
                nombre=tipo_gasto_defecto
            )
            db.add(nuevo_tipo)

    proveedor = Proveedor(
        nombre=nombre.strip(),
        cif=cif,
        telefono=telefono,
        email=email,
        tipo_gasto_defecto=tipo_gasto_defecto,
        tiene_retencion=(tiene_retencion == "si"),
        porcentaje_retencion_defecto=(
            porcentaje_retencion_defecto
            if tiene_retencion == "si"
            else 0
        )
    )

    db.add(proveedor)
    db.commit()

    return RedirectResponse(
        url="/gastos/proveedores",
        status_code=303
    )
@router.get("")
def listado_proveedores(
    request: Request,
    db: Session = Depends(get_db)
):
    proveedores = (
        db.query(Proveedor)
        .order_by(Proveedor.nombre.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="gastos/proveedores/listado.html",
        context={
            "proveedores": proveedores
        }
    )
@router.get("/editar/{proveedor_id}")
def editar_proveedor(
    proveedor_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    tipos_gasto = (
        db.query(TipoGasto)
        .order_by(TipoGasto.nombre)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="gastos/proveedores/editar.html",
        context={
            "proveedor": proveedor,
            "tipos_gasto": tipos_gasto
        }
    )


@router.post("/editar/{proveedor_id}")
def guardar_edicion_proveedor(
    proveedor_id: int,
    nombre: str = Form(...),
    cif: str = Form(None),
    telefono: str = Form(None),
    email: str = Form(None),
    tipo_gasto_defecto: str = Form(None),
    tiene_retencion: str = Form("no"),
    porcentaje_retencion_defecto: float = Form(0),
    db: Session = Depends(get_db)
):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    proveedor.nombre = nombre.strip()
    proveedor.cif = cif
    proveedor.telefono = telefono
    proveedor.email = email
    proveedor.tipo_gasto_defecto = tipo_gasto_defecto
    proveedor.tiene_retencion = tiene_retencion == "si"
    proveedor.porcentaje_retencion_defecto = (
        porcentaje_retencion_defecto if tiene_retencion == "si" else 0
    )

    db.commit()

    return RedirectResponse(
        url="/gastos/proveedores",
        status_code=303
    )


@router.post("/borrar/{proveedor_id}")
def borrar_proveedor(
    proveedor_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    proveedor = (
        db.query(Proveedor)
        .filter(Proveedor.id == proveedor_id)
        .first()
    )

    proveedores = (
        db.query(Proveedor)
        .order_by(Proveedor.nombre)
        .all()
    )

    if not proveedor:
        return templates.TemplateResponse(
            request=request,
            name="gastos/proveedores/listado.html",
            context={
                "proveedores": proveedores,
                "error": "Proveedor no encontrado."
            }
        )

    gastos_asociados = (
        db.query(Gasto)
        .filter(Gasto.proveedor == proveedor.nombre)
        .count()
    )

    if gastos_asociados > 0:
        return templates.TemplateResponse(
            request=request,
            name="gastos/proveedores/listado.html",
            context={
                "proveedores": proveedores,
                "error": (
                    f'No se puede borrar "{proveedor.nombre}". '
                    f'Existen {gastos_asociados} gasto'
                    f'{"s" if gastos_asociados != 1 else ""} asociado'
                    f'{"s" if gastos_asociados != 1 else ""}.'
                )
            }
        )

    db.delete(proveedor)
    db.commit()

    return RedirectResponse(
        url="/gastos/proveedores",
        status_code=303
    )