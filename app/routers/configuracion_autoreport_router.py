from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.configuracion_autoreport import ConfiguracionAutoreport
from app.services.autoreport_service import ejecutar_autoreport
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")


router = APIRouter()


def obtener_configuracion(db: Session) -> ConfiguracionAutoreport:
    cfg = db.query(ConfiguracionAutoreport).first()

    if not cfg:
        cfg = ConfiguracionAutoreport(
            activo=True,
            hora_envio="21:00",
            destinatarios="",
            dias_adelante=1,
            dias_ocupacion=7
        )
        db.add(cfg)
        db.commit()
        db.refresh(cfg)

    return cfg


@router.get("/dashboard/configuracion/autoreports")
def configurar_autoreports(
    request: Request,
    db: Session = Depends(get_db)
):
    cfg = obtener_configuracion(db)

    return templates.TemplateResponse(
        request=request,
        name="configuracion/autoreports.html",
        context={
            "cfg": cfg,
            "mensaje": request.query_params.get("mensaje"),
            "error": request.query_params.get("error"),
        }
    )


@router.post("/dashboard/configuracion/autoreports")
def guardar_autoreports(
    activo: str | None = Form(None),
    hora_envio: str = Form(...),
    destinatarios: str = Form(...),
    dias_adelante: int = Form(...),
    dias_ocupacion: int = Form(...),
    db: Session = Depends(get_db)
):
    cfg = obtener_configuracion(db)

    cfg.activo = activo == "on"
    cfg.hora_envio = hora_envio
    cfg.destinatarios = destinatarios.strip()
    cfg.dias_adelante = dias_adelante
    cfg.dias_ocupacion = dias_ocupacion

    db.commit()

    return RedirectResponse(
        url="/dashboard/configuracion/autoreports?mensaje=Configuración guardada",
        status_code=303
    )


@router.post("/dashboard/configuracion/autoreports/test")
def probar_autoreport():
    try:
        ejecutar_autoreport()
        return RedirectResponse(
            url="/dashboard/configuracion/autoreports?mensaje=Correo de prueba enviado",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/dashboard/configuracion/autoreports?error={str(e)}",
            status_code=303
        )