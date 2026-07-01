from fastapi import APIRouter
import os
import smtplib

from app.services.autoreport_service import ejecutar_autoreport

router = APIRouter()


@router.get("/admin/test-autoreport")
def test_autoreport():
    ejecutar_autoreport()
    return {"ok": True, "mensaje": "Autoreport ejecutado"}


@router.get("/admin/test-smtp")
def test_smtp():
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    print("SMTP_HOST:", smtp_host)
    print("SMTP_PORT:", smtp_port)
    print("SMTP_USER:", smtp_user)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(smtp_user, smtp_password)

    return {"ok": True, "mensaje": "Conexión SMTP correcta"}