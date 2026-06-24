from pathlib import Path
from datetime import datetime


from app.verifactu.config import LOG_DIR

LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_verifactu(mensaje: str):

    fecha = datetime.now().strftime("%Y-%m-%d")

    log_file = LOG_DIR / f"verifactu_{fecha}.log"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a", encoding="utf-8") as f:

        f.write(f"[{timestamp}] {mensaje}\n")