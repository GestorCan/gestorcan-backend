import hashlib
from pathlib import Path
import shutil
import os

from app.verifactu.config import SIGNED_DIR

from pathlib import Path
import os

from dotenv import load_dotenv
from lxml import etree
from signxml import XMLSigner, methods

from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates
)
from cryptography.hazmat.primitives import serialization




SIGNED_DIR.mkdir(parents=True, exist_ok=True)


def firmar_xml_simulado(xml_path: str):

    with open(xml_path, "rb") as f:
        contenido = f.read()

    firma = hashlib.sha256(contenido).hexdigest()

    nombre = os.path.basename(xml_path)

    signed_path = SIGNED_DIR / nombre

    shutil.copy(xml_path, signed_path)

    return {
        "signed_path": str(signed_path),
        "firma": firma
    }



def firmar_xml_real(xml_path: str):

    load_dotenv()

    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    cert_path_env = os.getenv("AEAT_CERT_PATH")
    cert_password = os.getenv("AEAT_CERT_PASSWORD")

    cert_path = BASE_DIR / cert_path_env

    xml_path = Path(xml_path)

    if not xml_path.is_absolute():
        xml_path = BASE_DIR / xml_path

    with open(cert_path, "rb") as f:
        pfx_data = f.read()

    private_key, cert, additional_certs = (
        load_key_and_certificates(
            pfx_data,
            cert_password.encode()
        )
    )

    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    cert_pem = cert.public_bytes(
        encoding=serialization.Encoding.PEM
    )

    tree = etree.parse(str(xml_path))
    root = tree.getroot()

    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256"
    )

    signed_root = signer.sign(
        root,
        key=key_pem,
        cert=cert_pem
    )

    nombre = os.path.basename(str(xml_path))

    signed_path = SIGNED_DIR / nombre

    etree.ElementTree(signed_root).write(
        str(signed_path),
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=False
    )

    return {
        "signed_path": str(signed_path),
        "firma": "XMLDSIG"
    }