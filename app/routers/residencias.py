
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.residencias import Residencia
from app.schemas.residencia import (ResidenciaResponse,ResidenciaUpdate)
from app.crud.residencias import (obtener_residencia,actualizar_residencia)
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import os
import shutil






router = APIRouter(prefix="/residencias", tags=["Residencias"])




@router.post("/{residencia_id}/logo")
def subir_logo_residencia(
    residencia_id: int,
    logo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    residencia = obtener_residencia(db, residencia_id)

    if not residencia:
        raise HTTPException(status_code=404, detail="Residencia no encontrada")

    carpeta = "static/logos"
    os.makedirs(carpeta, exist_ok=True)

    extension = logo.filename.split(".")[-1]
    nombre_archivo = f"residencia_{residencia_id}.{extension}"
    ruta_archivo = os.path.join(carpeta, nombre_archivo)

    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(logo.file, buffer)

    residencia.logo_url = f"/static/logos/{nombre_archivo}"

    db.commit()
    db.refresh(residencia)

    return {
        "ok": True,
        "logo_url": residencia.logo_url
    }


@router.get("/test")
def crear_residencia_test(db: Session = Depends(get_db)):

    residencia = Residencia(
        nombre="Residencia Canina El Bosque",
        cif="B12345678",
        direccion="C/ Pinos 12, Madrid",
        telefono="600123123",
        email="info@elbosque.com",
        logo_url="static/logos/logo.png"   # 👈 ESTE ES EL PASO 2
    )

    db.add(residencia)
    db.commit()
    db.refresh(residencia)

    return residencia



@router.post("/{residencia_id}/logo")
def subir_logo_residencia(
    residencia_id: int,
    logo: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    residencia = obtener_residencia(
        db,
        residencia_id
    )

    if not residencia:

        raise HTTPException(
            status_code=404,
            detail="Residencia no encontrada"
        )

    carpeta = "static/logos"

    os.makedirs(
        carpeta,
        exist_ok=True
    )

    extension = logo.filename.split(".")[-1]

    nombre_archivo = (
        f"residencia_{residencia_id}.{extension}"
    )

    ruta_archivo = os.path.join(
        carpeta,
        nombre_archivo
    )

    with open(ruta_archivo, "wb") as buffer:

        shutil.copyfileobj(
            logo.file,
            buffer
        )

    residencia.logo_url = (
        f"/static/logos/{nombre_archivo}"
    )

    db.commit()
    db.refresh(residencia)

    return {
        "ok": True,
        "logo_url": residencia.logo_url
    }





@router.get("/{residencia_id}",
    response_model=ResidenciaResponse
)
def obtener(
    residencia_id: int,
    db: Session = Depends(get_db)
):

    residencia = obtener_residencia(
        db,
        residencia_id
    )

    if not residencia:
        raise HTTPException(
            status_code=404,
            detail="Residencia no encontrada"
        )

    return residencia


@router.put("/{residencia_id}",
    response_model=ResidenciaResponse
)
def actualizar(
    residencia_id: int,
    datos: ResidenciaUpdate,
    db: Session = Depends(get_db)
):

    residencia = actualizar_residencia(
        db,
        residencia_id,
        datos
    )

    if not residencia:
        raise HTTPException(
            status_code=404,
            detail="Residencia no encontrada"
        )

    return residencia