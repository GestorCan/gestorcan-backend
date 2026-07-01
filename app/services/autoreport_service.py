from datetime import date, timedelta

from app.services.email_resend_service import enviar_email_resend
from app.services.report_trabajo_service import generar_informe_trabajo_pdf
from app.services.report_ocupacion_service import generar_informe_ocupacion_pdf
from app.database import SessionLocal
from app.models.configuracion_autoreport import ConfiguracionAutoreport


def ejecutar_autoreport():

    db = SessionLocal()

    try:
        cfg = db.query(ConfiguracionAutoreport).first()

        if not cfg:
            print("No existe configuración de autoreports.")
            return

        if not cfg.activo:
            print("Autoreports desactivado desde configuración.")
            return

        dias_adelante = cfg.dias_adelante or 1
        fecha_trabajo = date.today() + timedelta(days=dias_adelante)

        pdf_trabajo = generar_informe_trabajo_pdf(
            db=db,
            fecha=fecha_trabajo
        )

        pdf_ocupacion = generar_informe_ocupacion_pdf(
            db=db
        )

        lista_destinatarios = [
            email.strip()
            for email in (cfg.destinatarios or "").split(",")
            if email.strip()
        ]

        if not lista_destinatarios:
            raise ValueError("No hay destinatarios configurados en Autoreports")

        asunto = f"GestorCan - Planificación de mañana {fecha_trabajo.strftime('%d/%m/%Y')}"

        cuerpo = f"""
GestorCan - Planificación diaria

Fecha de trabajo: {fecha_trabajo.strftime('%d/%m/%Y')}

Adjuntos:
- Informe de Trabajo de mañana
- Informe de Ocupación próximos 7 días
"""

        enviar_email_resend(
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