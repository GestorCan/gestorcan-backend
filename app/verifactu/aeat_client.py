from datetime import datetime
from pathlib import Path
import os

from dotenv import load_dotenv
from lxml import etree
from requests_pkcs12 import post

from app.verifactu.constants import ESTADO_SIMULADO
from app.verifactu.settings import envio_real_activado


load_dotenv()


URL_TEST = (
    "https://prewww1.aeat.es/"
    "wlpl/TIKE-CONT/ws/SistemaFacturacion/VerifactuSOAP"
)

URL_PROD = (
    "https://www1.agenciatributaria.gob.es/"
    "wlpl/TIKE-CONT/ws/SistemaFacturacion/VerifactuSOAP"
)

NS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"

NS_RESP = {
    "env": "http://schemas.xmlsoap.org/soap/envelope/",
    "tikR": "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/RespuestaSuministro.xsd",
    "tik": "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroInformacion.xsd",
}


def base_dir():
    return Path(__file__).resolve().parent.parent.parent


def resolver_ruta(ruta: str) -> Path:
    ruta_path = Path(ruta)

    if ruta_path.is_absolute():
        return ruta_path

    return base_dir() / ruta_path


def obtener_url_aeat():
    entorno = os.getenv("VERIFACTU_ENV", "test").lower()

    if entorno == "prod":
        return URL_PROD

    return URL_TEST


def crear_soap_envelope(xml_path: str) -> bytes:
    xml_factura = etree.parse(str(resolver_ruta(xml_path))).getroot()

    envelope = etree.Element(
        f"{{{NS_SOAP}}}Envelope",
        nsmap={"soapenv": NS_SOAP}
    )

    body = etree.SubElement(envelope, f"{{{NS_SOAP}}}Body")
    body.append(xml_factura)

    return etree.tostring(
        envelope,
        encoding="utf-8",
        xml_declaration=True
    )


def texto_xml(root, xpath: str):
    elem = root.find(xpath, NS_RESP)

    if elem is None:
        return None

    return elem.text


def parsear_respuesta_aeat(texto_respuesta: str, status_code: int):
    root = etree.fromstring(texto_respuesta.encode("utf-8"))

    fault = texto_xml(root, ".//env:Fault/faultstring")

    if fault:
        return {
            "ok": False,
            "estado": "ERROR",
            "fecha_envio": datetime.now(),
            "csv": None,
            "estado_envio": None,
            "estado_registro": "ERROR",
            "codigo_error": None,
            "descripcion_error": fault,
            "timestamp_presentacion": None,
            "respuesta": texto_respuesta,
            "status_code": status_code,
        }

    csv = texto_xml(root, ".//tikR:CSV")
    estado_envio = texto_xml(root, ".//tikR:EstadoEnvio")
    estado_registro = texto_xml(root, ".//tikR:EstadoRegistro")
    codigo_error = texto_xml(root, ".//tikR:CodigoErrorRegistro")
    descripcion_error = texto_xml(root, ".//tikR:DescripcionErrorRegistro")
    timestamp = texto_xml(root, ".//tik:TimestampPresentacion")

    ok = estado_envio == "Correcto" and estado_registro == "Correcto"

    return {
        "ok": ok,
        "estado": estado_registro or estado_envio or "SIN_ESTADO",
        "fecha_envio": datetime.now(),
        "csv": csv,
        "estado_envio": estado_envio,
        "estado_registro": estado_registro,
        "codigo_error": codigo_error,
        "descripcion_error": descripcion_error,
        "timestamp_presentacion": timestamp,
        "respuesta": texto_respuesta,
        "status_code": status_code,
    }


def enviar_registro_verifactu_simulado(xml_path: str):
    ahora = datetime.now()

    csv_simulado = (
        "SIM-"
        + ahora.strftime("%Y%m%d%H%M%S")
    )

    return {
        "ok": True,
        "estado": ESTADO_SIMULADO,
        "fecha_envio": ahora,

        "csv": csv_simulado,
        "estado_envio": ESTADO_SIMULADO,
        "estado_registro": "AceptadoSimulado",

        "codigo_error": None,
        "descripcion_error": None,
        "timestamp_presentacion": ahora,

        "respuesta": (
            "Registro VeriFactu simulado correctamente. "
            f"No enviado a AEAT. XML: {xml_path}"
        ),

        "status_code": None,
    }


def enviar_registro_verifactu_real(xml_path: str):
    cert_path = resolver_ruta(os.getenv("AEAT_CERT_PATH"))
    cert_password = os.getenv("AEAT_CERT_PASSWORD")

    soap_xml = crear_soap_envelope(xml_path)

    response = post(
        obtener_url_aeat(),
        data=soap_xml,
        headers={
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": ""
        },
        pkcs12_filename=str(cert_path),
        pkcs12_password=cert_password,
        timeout=60
    )

    return parsear_respuesta_aeat(
        response.text,
        response.status_code
    )


def enviar_registro_verifactu(xml_path: str):
    if envio_real_activado():
        return enviar_registro_verifactu_real(xml_path)

    return enviar_registro_verifactu_simulado(xml_path)