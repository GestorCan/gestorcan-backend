import os
import base64
from pathlib import Path
import requests


def enviar_email_resend(
    asunto: str,
    cuerpo: str,
    destinatarios: list[str],
    adjuntos: list[str] | None = None
):
    api_key = os.getenv("RESEND_API_KEY")
    email_from = os.getenv("EMAIL_FROM")

    if not api_key:
        raise RuntimeError("Falta RESEND_API_KEY")

    if not email_from:
        raise RuntimeError("Falta EMAIL_FROM")

    attachments = []

    for adjunto in adjuntos or []:
        ruta = Path(adjunto)

        if not ruta.exists():
            raise FileNotFoundError(f"No existe el adjunto: {ruta}")

        attachments.append({
            "filename": ruta.name,
            "content": base64.b64encode(ruta.read_bytes()).decode("utf-8")
        })

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": email_from,
            "to": destinatarios,
            "subject": asunto,
            "text": cuerpo,
            "attachments": attachments,
        },
        timeout=30,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"Error Resend {response.status_code}: {response.text}")

    return response.json()