from pathlib import Path
import os

from dotenv import load_dotenv
from lxml import etree
from signxml import XMLSigner, methods
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.hazmat.primitives import serialization


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

CERT_PATH = BASE_DIR / os.getenv("AEAT_CERT_PATH")
CERT_PASSWORD = os.getenv("AEAT_CERT_PASSWORD")

XML_ORIGEN = BASE_DIR / "app" / "verifactu" / "storage" / "xml" / "2026-000001.xml"
XML_FIRMADO = BASE_DIR / "app" / "verifactu" / "storage" / "signed" / "2026-000001_firmado.xml"

XML_FIRMADO.parent.mkdir(parents=True, exist_ok=True)


with open(CERT_PATH, "rb") as f:
    pfx_data = f.read()

private_key, cert, additional_certs = load_key_and_certificates(
    pfx_data,
    CERT_PASSWORD.encode()
)

key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

cert_pem = cert.public_bytes(
    encoding=serialization.Encoding.PEM
)

tree = etree.parse(str(XML_ORIGEN))
root = tree.getroot()

signer = XMLSigner(
    method=methods.enveloped,
    signature_algorithm="rsa-sha256",
    digest_algorithm="sha256",
    c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"
)

signed_root = signer.sign(
    root,
    key=key_pem,
    cert=cert_pem
)

etree.ElementTree(signed_root).write(
    str(XML_FIRMADO),
    encoding="utf-8",
    xml_declaration=True,
    pretty_print=False
)

print("XML firmado correctamente:")
print(XML_FIRMADO)