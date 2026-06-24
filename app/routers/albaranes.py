# routes/albaranes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.services.albaranes_service import listar_albaranes
router = APIRouter(prefix="/albaranes", tags=["Albaranes"])
from app.services.albaranes_service import regenerar_pdf_albaran
MEDIA_ALBARANES = Path("media/albaranes")
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.albaranes_service import (
    obtener_ruta_pdf_albaran,
    regenerar_pdf_albaran
)




@router.get("/")
def get_albaranes(cliente: str | None = None, fecha: str | None = None):
    return listar_albaranes(cliente, fecha)


@router.get("/{estancia_id}/pdf")
def ver_pdf_albaran(estancia_id: int):
    ruta_pdf = obtener_ruta_pdf_albaran(estancia_id)

    if not ruta_pdf or not Path(ruta_pdf).exists():
        ruta_pdf = regenerar_pdf_albaran(estancia_id)

    if not ruta_pdf or not Path(ruta_pdf).exists():
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    return FileResponse(
        ruta_pdf,
        media_type="application/pdf",
        filename=Path(ruta_pdf).name
    )


@router.post("/{estancia_id}/regenerar")
def regenerar_pdf_albaran_endpoint(estancia_id: int):
    ruta_pdf = regenerar_pdf_albaran(estancia_id)

    if not ruta_pdf:
        raise HTTPException(status_code=404, detail="Estancia no encontrada")

    return {
        "ok": True,
        "mensaje": "PDF regenerado correctamente",
        "ruta": ruta_pdf
    }