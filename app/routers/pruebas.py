from fastapi import APIRouter
from app.services.autoreport_service import ejecutar_autoreport

router = APIRouter()


@router.get("/admin/test-autoreport")
def test_autoreport():

    ejecutar_autoreport()

    return {
        "ok": True,
        "mensaje": "Autoreport ejecutado"
    }