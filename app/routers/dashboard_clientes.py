from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.clientes import Cliente
from fastapi import Form
from fastapi.responses import RedirectResponse
from app.utils.validadores_fiscales import (
    limpiar_documento_fiscal,
    validar_nif_nie
)
from fastapi import HTTPException
from typing import Optional
from sqlalchemy import or_
from app.models.clientes import Cliente
from app.models.mascotas import Mascota
from app.models.estancia import Estancia




router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





@router.post("/dashboard/clientes/{cliente_id}/eliminar")
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        return RedirectResponse(
            url="/dashboard/clientes?error=cliente_no_encontrado",
            status_code=303
        )

    mascotas_asociadas = db.query(Mascota).filter(
        Mascota.cliente_id == cliente_id
    ).count()

    if mascotas_asociadas > 0:
        return RedirectResponse(
            url="/dashboard/clientes?error=cliente_con_mascotas",
            status_code=303
        )

    estancias_asociadas = db.query(Estancia).filter(
        Estancia.cliente_id == cliente_id
    ).count()

    if estancias_asociadas > 0:
        return RedirectResponse(
            url="/dashboard/clientes?error=cliente_con_estancias",
            status_code=303
        )

    db.delete(cliente)
    db.commit()

    return RedirectResponse(
        url="/dashboard/clientes?ok=cliente_eliminado",
        status_code=303
    )
@router.get("/dashboard/clientes/nuevo")
def nuevo_cliente_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="clientes/nuevo.html",
        context={}
    )
@router.post("/dashboard/clientes/{cliente_id}/editar")
def guardar_edicion_cliente(
    cliente_id: int,
    request: Request,
    nombre: str = Form(...),
    apellidos: str = Form(None),
    dni: str = Form(None),
    tipo_documento: str = Form("NIF"),
    telefono: str = Form(None),
    email: str = Form(None),
    direccion: str = Form(None),
    codigo_postal: str = Form(None),
    poblacion: str = Form(None),
    provincia: str = Form(None),
    redes_sociales: str = Form(None),
    observaciones: str = Form(None),
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        return RedirectResponse(url="/dashboard/clientes", status_code=303)

    if dni:
        dni = limpiar_documento_fiscal(dni)

        if tipo_documento in ("NIF", "NIE"):
            if not validar_nif_nie(dni):
                return templates.TemplateResponse(
                    request=request,
                    name="clientes/editar.html",
                    context={
                        "cliente": cliente,
                        "error": "El NIF/NIE introducido no es válido."
                    },
                    status_code=400
                )

        cliente_duplicado = (
            db.query(Cliente)
            .filter(
                Cliente.dni == dni,
                Cliente.id != cliente_id
            )
            .first()
        )

        if cliente_duplicado:
            return templates.TemplateResponse(
                request=request,
                name="clientes/editar.html",
                context={
                    "cliente": cliente,
                    "error": "Ya existe otro cliente con ese documento."
                },
                status_code=400
            )
        dni = limpiar_documento_fiscal(dni)

        if not dni:
            return templates.TemplateResponse(
                request=request,
                name="clientes/editar.html",
                context={
                    "cliente": cliente,
                    "error": "El número de documento es obligatorio."
                },
                status_code=400
            )

    cliente.nombre = nombre
    cliente.apellidos = apellidos
    cliente.dni = dni
    cliente.tipo_documento = tipo_documento
    cliente.telefono = telefono
    cliente.email = email
    cliente.direccion = direccion
    cliente.codigo_postal = codigo_postal
    cliente.poblacion = poblacion
    cliente.provincia = provincia
    cliente.redes_sociales = redes_sociales
    cliente.observaciones = observaciones

    db.commit()

    return RedirectResponse(url="/dashboard/clientes", status_code=303)
@router.get("/dashboard/clientes/{cliente_id}/editar")
def editar_cliente_form(
    cliente_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        return RedirectResponse(url="/dashboard/clientes", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="clientes/editar.html",
        context={
            "cliente": cliente
        }
    )

@router.get("/dashboard/clientes/{cliente_id}/creado")
def cliente_creado(
    cliente_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        return RedirectResponse(url="/dashboard/clientes", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="clientes/creado.html",
        context={
            "cliente": cliente
        }
    )



@router.post("/dashboard/clientes/nuevo")
def crear_cliente_desde_dashboard(
    request: Request,
    nombre: str = Form(...),
    apellidos: str = Form(None),
    dni: str = Form(...),
    tipo_documento: str = Form("NIF"),
    telefono: str = Form(None),
    email: str = Form(None),
    direccion: str = Form(None),
    codigo_postal: str = Form(None),
    poblacion: str = Form(None),
    provincia: str = Form(None),
    redes_sociales: str = Form(None),
    observaciones: str = Form(None),
    db: Session = Depends(get_db),

):
    dni = limpiar_documento_fiscal(dni)

    if not dni:
        return templates.TemplateResponse(
            request=request,
            name="clientes/nuevo.html",
            context={
                "error": "El número de documento es obligatorio."
            },
            status_code=400
        )

    if tipo_documento in ("NIF", "NIE"):
        if not validar_nif_nie(dni):
            return templates.TemplateResponse(
                request=request,
                name="clientes/nuevo.html",
                context={
                    "error": "El documento introducido no es válido."
                },
                status_code=400
            )
    cliente_existente = db.query(Cliente).filter(
        Cliente.dni == dni
    ).first()

    if cliente_existente:
        return templates.TemplateResponse(
            request=request,
            name="clientes/nuevo.html",
            context={
                "error": f"Ya existe un cliente con el documento {dni}."
            },
            status_code=400
        )

    nuevo_cliente = Cliente(
        nombre=nombre,
        apellidos=apellidos,
        dni=dni,
        tipo_documento=tipo_documento,
        telefono=telefono,
        email=email,
        direccion=direccion,
        codigo_postal=codigo_postal,
        poblacion=poblacion,
        provincia=provincia,
        redes_sociales=redes_sociales,
        observaciones=observaciones
    )

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return RedirectResponse(
        url=f"/dashboard/clientes/{nuevo_cliente.id}/creado",
        status_code=303
    )



@router.get("/dashboard/clientes")
def dashboard_clientes(
    request: Request,
    buscar: Optional[str] = None,
    error: Optional[str] = None,
    ok: Optional[str] = None,
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if not limit:
        limit = 100
    query = db.query(Cliente)
    print("BUSCAR CLIENTES:", buscar)

    if buscar:
        texto = f"%{buscar}%"
        query = query.filter(
            or_(
                Cliente.nombre.ilike(texto),
                Cliente.apellidos.ilike(texto),
                Cliente.dni.ilike(texto),
                Cliente.telefono.ilike(texto),
                Cliente.email.ilike(texto),
            )
        )

    total = query.count()

    clientes = (
        query
        .order_by(Cliente.nombre.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="clientes/dashboard.html",
        context={
            "clientes": clientes,
            "buscar": buscar or "",
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "error": error,
            "ok": ok,
        }
    )