from pathlib import Path
import os

from dotenv import load_dotenv
from requests_pkcs12 import post

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

cert_path = BASE_DIR / os.getenv("AEAT_CERT_PATH")
cert_password = os.getenv("AEAT_CERT_PASSWORD")

url = (
    "https://prewww1.aeat.es/"
    "wlpl/TIKE-CONT/ws/SistemaFacturacion/VerifactuSOAP"
)

soap = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope
 xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
 <soapenv:Body>
 </soapenv:Body>
</soapenv:Envelope>
"""

response = post(
    url,
    data=soap.encode("utf-8"),
    headers={
        "Content-Type": "text/xml; charset=utf-8"
    },
    pkcs12_filename=str(cert_path),
    pkcs12_password=cert_password,
    timeout=30
)

print("STATUS:", response.status_code)
print()
print(response.text[:3000])