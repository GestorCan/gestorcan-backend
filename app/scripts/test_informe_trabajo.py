from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

from app.database import SessionLocal
from app.services.report_trabajo_service import generar_informe_trabajo_pdf

db = SessionLocal()

try:
    archivo = generar_informe_trabajo_pdf(db)
    print("PDF generado:", archivo)
finally:
    db.close()