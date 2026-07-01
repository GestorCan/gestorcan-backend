import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

from app.services.email_service import enviar_email


pdf_prueba = BASE_DIR / "app" / "reports" / "autoreports" / "informe_trabajo_29-06-2026.pdf"

print("PDF:", pdf_prueba)
print("EXISTE:", pdf_prueba.exists())

enviar_email(
    asunto="Prueba Autoreport GestorCan con PDF",
    cuerpo="""
Hola,

Este es un correo de prueba del sistema
de autoreports de GestorCan.

Saludos.
""",
    destinatarios=[
        "cualqueda2505@gmail.com"
    ],
    adjuntos=[
        str(pdf_prueba)
    ]
)