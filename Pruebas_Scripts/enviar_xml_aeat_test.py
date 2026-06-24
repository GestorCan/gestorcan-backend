from pathlib import Path
import os

from dotenv import load_dotenv
from lxml import etree
from requests_pkcs12 import post

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
    / "R2026-000002.xml"
)

URL_TEST = (
    "https://prewww1.aeat.es/"
    "wlpl/TIKE-CONT/ws/SistemaFacturacion/VerifactuSOAP"
)

NS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"

xml_factura = etree.parse(str(XML_FIRMADO)).getroot()

envelope = etree.Element(
    f"{{{NS_SOAP}}}Envelope",
    nsmap={"soapenv": NS_SOAP}
)

body = etree.SubElement(envelope, f"{{{NS_SOAP}}}Body")
body.append(xml_factura)

soap_xml = etree.tostring(
    envelope,
    encoding="utf-8",
    xml_declaration=True
)

response = post(
    URL_TEST,
    data=soap_xml,
    headers={
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": ""
    },
    pkcs12_filename=str(CERT_PATH),
    pkcs12_password=CERT_PASSWORD,
    timeout=60
)

print("STATUS:", response.status_code)
print()
print(response.text)