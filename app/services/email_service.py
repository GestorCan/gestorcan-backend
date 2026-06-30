import os
import smtplib
from email.message import EmailMessage


def enviar_email(
    asunto: str,
    cuerpo: str,
    destinatarios: list[str],
    adjuntos: list[str] | None = None
):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM") or smtp_user

    print("SMTP_HOST:", smtp_host)
    print("SMTP_PORT:", smtp_port)
    print("SMTP_USER:", smtp_user)
    print("SMTP_FROM:", smtp_from)

    if not smtp_host or not smtp_user or not smtp_password:
        raise ValueError("Faltan variables SMTP en el .env")

    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = smtp_from
    msg["To"] = ", ".join(destinatarios)
    msg.set_content(cuerpo)

    if adjuntos:
        for archivo in adjuntos:
            with open(archivo, "rb") as f:
                datos = f.read()

            nombre = os.path.basename(archivo)

            msg.add_attachment(
                datos,
                maintype="application",
                subtype="pdf",
                filename=nombre
            )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(msg)

    print("Email enviado correctamente")