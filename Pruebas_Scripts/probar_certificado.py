from pathlib import Path
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from dotenv import load_dotenv
import os

load_dotenv()

ruta = os.getenv("AEAT_CERT_PATH")
password = os.getenv("AEAT_CERT_PASSWORD")

base_dir = Path(__file__).resolve().parent.parent
ruta_cert = base_dir / ruta

print("Certificado:", ruta_cert)

with open(ruta_cert, "rb") as f:
    pfx_data = f.read()

clave, certificado, adicionales = load_key_and_certificates(
    pfx_data,
    password.encode()
)

print("CERTIFICADO LEÍDO CORRECTAMENTE")
print("Sujeto:", certificado.subject.rfc4514_string())
print("Emisor:", certificado.issuer.rfc4514_string())

print("Número de serie:", certificado.serial_number)
print("Válido desde:", certificado.not_valid_before_utc)
print("Válido hasta:", certificado.not_valid_after_utc)

print("Clave privada encontrada:", clave is not None)