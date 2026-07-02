from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent


# =========================
# MODOS
# =========================

VERIFACTU_ACTIVO = True

AEAT_MODO = "test"
# test | produccion


# =========================
# STORAGE
# =========================

STORAGE_DIR = BASE_DIR / "storage"

QR_DIR = STORAGE_DIR / "qr"

XML_DIR = STORAGE_DIR / "xml"

SIGNED_DIR = STORAGE_DIR / "signed"

LOG_DIR = BASE_DIR / "logs"


# =========================
# CERTIFICADOS
# =========================

CERT_DIR = BASE_DIR / "certificados"

CERT_PATH = CERT_DIR / "certificado.pfx"

CERT_PASSWORD = ""


# =========================
# AEAT
# =========================

AEAT_URL_TEST = "https://prewww2.aeat.es/"

AEAT_URL_PRODUCCION = "https://www2.agenciatributaria.gob.es/"




def verifactu_activado():
    return os.getenv(
        "VERIFACTU_ENABLED",
        "false"
    ).lower() == "true"


def firma_real_activada():
    return os.getenv(
        "VERIFACTU_FIRMA_REAL",
        "false"
    ).lower() == "true"


def verifactu_envio_real():
    return os.getenv(
        "VERIFACTU_ENVIO_REAL",
        "false"
    ).lower() == "true"


def entorno_verifactu():
    return os.getenv(
        "VERIFACTU_ENV",
        "test"
    )
def verifactu_envio_real():
    return os.getenv(
        "VERIFACTU_ENVIO_REAL",
        "false"
    ).lower() == "true"