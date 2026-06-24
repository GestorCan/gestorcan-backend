from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.mascotas import Mascota
from app.models.clientes import Cliente
from fastapi import File, UploadFile
import os
import shutil
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import joinedload


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def guardar_foto_mascota(foto: UploadFile, mascota_id: int):
    if not foto or not foto.filename:
        return None

    carpeta = f"static/img/mascotas/{mascota_id}"
    os.makedirs(carpeta, exist_ok=True)

    extension = os.path.splitext(foto.filename)[1]
    nombre_archivo = f"foto{extension}"
    ruta_fisica = os.path.join(carpeta, nombre_archivo)

    with open(ruta_fisica, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    return f"/static/img/mascotas/{mascota_id}/{nombre_archivo}"







@router.get("/dashboard/mascotas")
def dashboard_mascotas(
    request: Request,
    buscar: Optional[str] = None,
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if not limit:
        limit = 100

    query = (
        db.query(Mascota)
        .options(joinedload(Mascota.cliente))
    )

    if buscar:
        buscar = buscar.strip()
        texto = f"%{buscar}%"

        query = (
            query
            .join(Mascota.cliente)
            .filter(
                or_(
                    Mascota.nombre.ilike(texto),
                    Mascota.raza.ilike(texto),
                    Mascota.sexo.ilike(texto),
                    Cliente.nombre.ilike(texto),
                    Cliente.apellidos.ilike(texto),
                    Cliente.dni.ilike(texto),
                )
            )
        )

    total = query.count()

    mascotas = (
        query
        .order_by(Mascota.nombre.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="mascotas/dashboard.html",
        context={
            "mascotas": mascotas,
            "buscar": buscar or "",
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
        }
    )
@router.get("/dashboard/mascotas/nueva")
def nueva_mascota_form(
    request: Request,
    db: Session = Depends(get_db)
):
    clientes = db.query(Cliente).order_by(Cliente.nombre.asc()).all()

    return templates.TemplateResponse(
        request=request,
        name="mascotas/nueva.html",
        context={
            "clientes": clientes
        }
    )
@router.post("/dashboard/mascotas/nueva")
def crear_mascota_dashboard(
    cliente_id: int = Form(...),
    nombre: str = Form(...),
    raza: str = Form(None),
    sexo: str = Form(None),
    tamano: str = Form(None),
    edad: str = Form(None),
    numero_chip: str = Form(None),
    vacunas: str = Form(None),
    comportamiento_personas: str = Form(None),
    comportamiento_perros: str = Form(None),
    enfermedades_medicacion: str = Form(None),
    observaciones: str = Form(None),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    mascota = Mascota(
        cliente_id=cliente_id,
        nombre=nombre,
        raza=raza,
        sexo=sexo,
        tamano=tamano,
        edad=edad,
        numero_chip=numero_chip,
        vacunas=vacunas,
        comportamiento_personas=comportamiento_personas,
        comportamiento_perros=comportamiento_perros,
        enfermedades_medicacion=enfermedades_medicacion,
        observaciones=observaciones,

    )

    db.add(mascota)
    db.commit()
    db.refresh(mascota)

    foto_path = guardar_foto_mascota(foto, mascota.id)

    if foto_path:
        mascota.foto = foto_path
        db.commit()





    return RedirectResponse(
        url="/dashboard/mascotas",
        status_code=303
    )
@router.get("/dashboard/mascotas/{mascota_id}/editar")
def editar_mascota_form(
    mascota_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()
    clientes = db.query(Cliente).order_by(Cliente.nombre.asc()).all()

    if not mascota:
        return RedirectResponse(url="/dashboard/mascotas", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="mascotas/editar.html",
        context={
            "mascota": mascota,
            "clientes": clientes
        }
    )
@router.post("/dashboard/mascotas/{mascota_id}/editar")
def guardar_edicion_mascota(
    mascota_id: int,
    cliente_id: int = Form(...),
    nombre: str = Form(...),
    raza: str = Form(None),
    sexo: str = Form(None),
    tamano: str = Form(None),
    edad: str = Form(None),
    numero_chip: str = Form(None),
    vacunas: str = Form(None),
    comportamiento_personas: str = Form(None),
    comportamiento_perros: str = Form(None),
    enfermedades_medicacion: str = Form(None),
    observaciones: str = Form(None),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()

    if not mascota:
        return RedirectResponse(url="/dashboard/mascotas", status_code=303)

    mascota.cliente_id = cliente_id
    mascota.nombre = nombre
    mascota.raza = raza
    mascota.sexo = sexo
    mascota.tamano = tamano
    mascota.edad = edad
    mascota.numero_chip = numero_chip
    mascota.vacunas = vacunas
    mascota.comportamiento_personas = comportamiento_personas
    mascota.comportamiento_perros = comportamiento_perros
    mascota.enfermedades_medicacion = enfermedades_medicacion
    mascota.observaciones = observaciones

    foto_path = guardar_foto_mascota(foto, mascota.id)

    if foto_path:
        mascota.foto = foto_path

    db.commit()

    return RedirectResponse(
        url=f"/dashboard/clientes/{mascota.cliente_id}/editar",
        status_code=303
    )
@router.post("/dashboard/mascotas/{mascota_id}/eliminar")
def eliminar_mascota_dashboard(
    mascota_id: int,
    db: Session = Depends(get_db)
):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()

    if mascota:
        db.delete(mascota)
        db.commit()

    return RedirectResponse(
        url="/dashboard/mascotas",
        status_code=303
    )