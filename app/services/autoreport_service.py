from datetime import date, timedelta
import os

from app.services.email_service import enviar_email
from app.services.report_trabajo_service import generar_informe_trabajo_pdf
from app.services.report_ocupacion_service import generar_informe_ocupacion_pdf
from app.database import SessionLocal

def _env_bool(nombre: str, defecto: bool = False) -> bool:
    valor = os.getenv(nombre)
    if valor is None:
        return defecto
    return valor.lower() in ("true", "1", "yes", "si", "sí")


def ejecutar_autoreport():
    if not _env_bool("AUTOREPORTS_ACTIVO", False):
        print("Autoreports desactivado.")
        return

    db = SessionLocal()

    try:
        dias_adelante = int(os.getenv("AUTOREPORT_DIAS_ADELANTE", "1"))

        fecha_trabajo = date.today() + timedelta(days=dias_adelante)

        pdf_trabajo = generar_informe_trabajo_pdf(
            db=db,
            fecha=fecha_trabajo
        )

        pdf_ocupacion = generar_informe_ocupacion_pdf(
            db=db
        )

        asunto = f"GestorCan - Planificación de mañana {fecha_trabajo.strftime('%d/%m/%Y')}"

        destinatarios = os.getenv("AUTOREPORT_DESTINATARIOS", "")
        lista_destinatarios = [
            email.strip()
            for email in destinatarios.split(",")
            if email.strip()
        ]

        if not lista_destinatarios:
            raise ValueError("Falta AUTOREPORT_DESTINATARIOS en el .env")

        cuerpo = f"""
GestorCan - Planificación diaria

Fecha de trabajo: {fecha_trabajo.strftime('%d/%m/%Y')}

Adjuntos:
- Informe de Trabajo de mañana
- Informe de Ocupación próximos 7 días
"""

        enviar_email(
            asunto=asunto,
            cuerpo=cuerpo,
            destinatarios=lista_destinatarios,
            adjuntos=[
                pdf_trabajo,
                pdf_ocupacion
            ]
        )

        print("Autoreport enviado correctamente.")

    finally:
        db.close()