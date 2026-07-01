import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

from app.services.email_service import enviar_email

pdf_prueba = BASE_DIR / "reports" / "autoreports" / "informe_prueba.pdf"



print(Path(r"C:\Users\cualq\gestorcan-backend\app\reports\autoreports\informe_prueba.pdf").exists())