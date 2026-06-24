import os
from datetime import date


def env_bool(nombre: str, defecto: str = "false") -> bool:
    return os.getenv(nombre, defecto).lower() == "true"


def verifactu_activado() -> bool:
    return env_bool("VERIFACTU_ENABLED", "false")


def firma_real_activada() -> bool:
    return env_bool("VERIFACTU_FIRMA_REAL", "false")


def envio_real_activado() -> bool:
    envio_real = env_bool("VERIFACTU_ENVIO_REAL", "false")

    fecha_inicio = date.fromisoformat(
        os.getenv("VERIFACTU_FECHA_INICIO_REAL", "2027-01-01")
    )

    return envio_real and date.today() >= fecha_inicio


def entorno_verifactu() -> str:
    return os.getenv("VERIFACTU_ENV", "test").lower()