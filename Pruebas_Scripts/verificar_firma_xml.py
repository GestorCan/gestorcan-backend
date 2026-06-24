from pathlib import Path
import os

from dotenv import load_dotenv
from lxml import etree
from signxml import XMLVerifier
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.hazmat.primitives import serialization

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

CERT_PATH = BASE_DIR / os.getenv("AEAT_CERT_PATH")
CERT_PASSWORD = os.getenv("AEAT_CERT_PASSWORD")

XML_FIRMADO = (
    BASE_DIR
    / "app"
    / "verifactu"
    / "storage"
    / "signed"
    / "2026-000001_firmado.xml"
)

with open(CERT_PATH, "rb") as f:
    pfx_data = f.read()

private_key, cert, additional_certs = load_key_and_certificates(
    pfx_data,
    CERT_PASSWORD.encode()
)

cert_pem = cert.public_bytes(
    encoding=serialization.Encoding.PEM
)

parser = etree.XMLParser(remove_blank_text=True)
root = etree.parse(str(XML_FIRMADO), parser).getroot()

XMLVerifier().verify(
    root,
    x509_cert=cert_pem
)

print("FIRMA XML VERIFICADA CORRECTAMENTE")