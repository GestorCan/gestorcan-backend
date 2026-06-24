import os
import shutil
from PIL import Image

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.mascotas import Mascota
from app.schemas.mascotas import MascotaCreate, MascotaUpdate, MascotaOut


RUTA_BASE = "media/mascotas"
TAMANIO_MAX = 3 * 1024 * 1024
EXTENSIONES_PERMITIDAS = [".jpg", ".jpeg", ".png", ".webp"]


router = APIRouter(
    prefix="/mascotas",
    tags=["Mascotas"]
)


@router.post("/", response_model=MascotaOut)
def crear_mascota(mascota: MascotaCreate, db: Session = Depends(get_db)):
    nueva_mascota = Mascota(**mascota.model_dump())

    db.add(nueva_mascota)
    db.commit()
    db.refresh(nueva_mascota)

    return nueva_mascota


@router.get("/", response_model=list[MascotaOut])
def listar_mascotas(db: Session = Depends(get_db)):
    return db.query(Mascota).all()


@router.get("/{mascota_id}", response_model=MascotaOut)
def obtener_mascota(mascota_id: int, db: Session = Depends(get_db)):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()

    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    return mascota


@router.put("/{mascota_id}", response_model=MascotaOut)
def actualizar_mascota(
    mascota_id: int,
    datos_mascota: MascotaUpdate,
    db: Session = Depends(get_db)
):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()

    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    for campo, valor in datos_mascota.model_dump(exclude_unset=True).items():
        setattr(mascota, campo, valor)

    db.commit()
    db.refresh(mascota)

    return mascota


@router.post("/{mascota_id}/foto")
def subir_foto(
    mascota_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()

    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    _, extension = os.path.splitext(archivo.filename.lower())

    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(status_code=400, detail="Formato de imagen no permitido")

    contenido = archivo.file.read()

    if len(contenido) > TAMANIO_MAX:
        raise HTTPException(status_code=400, detail="Imagen demasiado grande. Máximo 3MB")

    carpeta = os.path.join(RUTA_BASE, str(mascota_id))
    os.makedirs(carpeta, exist_ok=True)

    nombre_archivo = f"principal{extension}"
    ruta_archivo = os.path.join(carpeta, nombre_archivo)

    with open(ruta_archivo, "wb") as f:
        f.write(contenido)

    ruta_miniatura = os.path.join(carpeta, f"thumb{extension}")

    imagen = Image.open(ruta_archivo)
    imagen.thumbnail((300, 300))
    imagen.save(ruta_miniatura)

    mascota.foto = ruta_archivo
    db.commit()
    db.refresh(mascota)

    return {
        "mensaje": "Foto subida correctamente",
        "foto": ruta_archivo,
        "miniatura": ruta_miniatura
    }


@router.delete("/{mascota_id}")
def borrar_mascota(mascota_id: int, db: Session = Depends(get_db)):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()

    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    carpeta = os.path.join(RUTA_BASE, str(mascota_id))

    if os.path.exists(carpeta):
        shutil.rmtree(carpeta)

    db.delete(mascota)
    db.commit()

    return {"mensaje": "Mascota eliminada correctamente junto con sus fotos"}

@router.get("/{mascota_id}/detalle")
def obtener_detalle_mascota(mascota_id: int, db: Session = Depends(get_db)):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()

    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    foto = mascota.foto

    if foto:
        foto = foto.replace("\\", "/")

        if not foto.startswith("/"):
            foto = "/" + foto

    return {
        "id": mascota.id,
        "nombre": mascota.nombre,
        "raza": getattr(mascota, "raza", ""),
        "sexo": getattr(mascota, "sexo", ""),
        "tamano": getattr(mascota, "tamano", ""),
        "vacunas": getattr(mascota, "vacunas", ""),
        "comportamiento_personas": getattr(mascota, "comportamiento_personas", ""),
        "comportamiento_perros": getattr(mascota, "comportamiento_perros", ""),
        "observaciones": getattr(mascota, "observaciones", ""),
        "foto_url": foto,

    }