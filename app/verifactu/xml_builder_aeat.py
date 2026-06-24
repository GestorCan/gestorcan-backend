from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree


NS_LR = "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroLR.xsd"
NS_SF = "https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/tike/cont/ws/SuministroInformacion.xsd"

ET.register_namespace("sfLR", NS_LR)
ET.register_namespace("sf", NS_SF)


def tag_lr(nombre: str) -> str:
    return f"{{{NS_LR}}}{nombre}"


def tag_sf(nombre: str) -> str:
    return f"{{{NS_SF}}}{nombre}"


def sub_sf(parent, nombre: str, texto=None):
    elem = SubElement(parent, tag_sf(nombre))
    if texto is not None:
        elem.text = str(texto)
    return elem


def fecha_aeat(fecha) -> str:
    return fecha.strftime("%d-%m-%Y")


def importe(valor) -> str:
    return f"{float(valor):.2f}"


def tipo_factura_aeat(factura) -> str:
    if getattr(factura, "tipo_factura", None) == "rectificativa":
        return "R1"
    return "F1"


def texto_residencia(residencia) -> str:
    return residencia.razon_social or residencia.nombre


def generar_xml_aeat(factura, residencia, cliente=None, factura_anterior=None):
    """
    Genera XML VeriFactu AEAT.

    Regla de namespaces:
    - sfLR: contenedores del libro/registro: RegFactuSistemaFacturacion, Cabecera, RegistroFactura.
    - sf: datos fiscales dentro de Cabecera y RegistroAlta.
    """

    # ==========================
    # RAÍZ
    # ==========================
    raiz = Element(tag_lr("RegFactuSistemaFacturacion"))

    # ==========================
    # CABECERA
    # ==========================
    cabecera = SubElement(raiz, tag_lr("Cabecera"))

    obligado = SubElement(cabecera, tag_sf("ObligadoEmision"))
    sub_sf(obligado, "NombreRazon", texto_residencia(residencia))
    sub_sf(obligado, "NIF", residencia.cif)

    # ==========================
    # REGISTRO FACTURA
    # ==========================
    registro_factura = SubElement(raiz, tag_lr("RegistroFactura"))
    registro_alta = SubElement(registro_factura, tag_sf("RegistroAlta"))

    # ==========================
    # REGISTRO ALTA
    # ==========================
    sub_sf(registro_alta, "IDVersion", "1.0")

    id_factura = SubElement(registro_alta, tag_sf("IDFactura"))
    sub_sf(id_factura, "IDEmisorFactura", residencia.cif)
    sub_sf(id_factura, "NumSerieFactura", factura.numero_factura)
    sub_sf(id_factura, "FechaExpedicionFactura", fecha_aeat(factura.fecha))

    sub_sf(registro_alta, "NombreRazonEmisor", texto_residencia(residencia))
    sub_sf(registro_alta, "TipoFactura", tipo_factura_aeat(factura))
    if getattr(factura, "tipo_factura", None) == "rectificativa":
        sub_sf(registro_alta, "TipoRectificativa", "I")



    descripcion = (
        factura.motivo_rectificacion
        if getattr(factura, "tipo_factura", None) == "rectificativa"
        else "Prestacion de servicios de residencia canina"
    )
    sub_sf(registro_alta, "DescripcionOperacion", descripcion)

    # ==========================
    # DESTINATARIOS
    # ==========================
    if cliente:
        destinatarios = SubElement(registro_alta, tag_sf("Destinatarios"))
        id_destinatario = SubElement(destinatarios, tag_sf("IDDestinatario"))

        nombre_cliente = f"{cliente.nombre or ''} {cliente.apellidos or ''}".strip()
        sub_sf(id_destinatario, "NombreRazon", nombre_cliente)
        sub_sf(id_destinatario, "NIF", cliente.dni)

    # ==========================
    # DESGLOSE IVA
    # ==========================
    desglose = SubElement(registro_alta, tag_sf("Desglose"))
    detalle = SubElement(desglose, tag_sf("DetalleDesglose"))

    sub_sf(detalle, "Impuesto", "01")
    sub_sf(detalle, "ClaveRegimen", "01")
    sub_sf(detalle, "CalificacionOperacion", "S1")
    sub_sf(detalle, "TipoImpositivo", "21.00")
    sub_sf(detalle, "BaseImponibleOimporteNoSujeto", importe(factura.base_imponible))
    sub_sf(detalle, "CuotaRepercutida", importe(factura.iva))

    sub_sf(registro_alta, "CuotaTotal", importe(factura.iva))
    sub_sf(registro_alta, "ImporteTotal", importe(factura.total))

    # ==========================
    # ENCADENAMIENTO
    # ==========================
    encadenamiento = SubElement(registro_alta, tag_sf("Encadenamiento"))

    if not getattr(factura, "hash_anterior", None):
        sub_sf(encadenamiento, "PrimerRegistro", "S")
    else:
        registro_anterior = SubElement(encadenamiento, tag_sf("RegistroAnterior"))
        sub_sf(registro_anterior, "IDEmisorFactura", residencia.cif)

        if factura_anterior:
            sub_sf(registro_anterior, "NumSerieFactura", factura_anterior.numero_factura)
            sub_sf(registro_anterior, "FechaExpedicionFactura", fecha_aeat(factura_anterior.fecha))
            sub_sf(registro_anterior, "Huella", factura_anterior.hash_actual)
        else:
            sub_sf(registro_anterior, "NumSerieFactura", "NO_LOCALIZADA")
            sub_sf(registro_anterior, "FechaExpedicionFactura", "NO_LOCALIZADA")
            sub_sf(registro_anterior, "Huella", factura.hash_anterior)

    # ==========================
    # SISTEMA INFORMÁTICO
    # ==========================
    sistema = SubElement(registro_alta, tag_sf("SistemaInformatico"))

    sub_sf(sistema, "NombreRazon", texto_residencia(residencia))
    sub_sf(sistema, "NIF", residencia.cif)
    sub_sf(sistema, "NombreSistemaInformatico", "GestorCan")
    sub_sf(sistema, "IdSistemaInformatico", "GC")
    sub_sf(sistema, "Version", "1.0.0")
    sub_sf(sistema, "NumeroInstalacion", "002")
    sub_sf(sistema, "TipoUsoPosibleSoloVerifactu", "S")
    sub_sf(sistema, "TipoUsoPosibleMultiOT", "N")
    sub_sf(sistema, "IndicadorMultiplesOT", "N")

    # Algunos XSD oficiales exigen este campo antes de TipoHuella.
    # Si tu XSD no lo acepta, lo quitamos en el siguiente ajuste.
    sub_sf(
        registro_alta,
        "FechaHoraHusoGenRegistro",
        factura.fecha_hora_huso_gen_registro,
    )

    sub_sf(registro_alta, "TipoHuella", "01")
    sub_sf(registro_alta, "Huella", factura.hash_actual)

    # ==========================
    # GUARDAR XML
    # ==========================
    carpeta = Path("app/verifactu/storage/xml")
    carpeta.mkdir(parents=True, exist_ok=True)

    ruta = carpeta / f"{factura.numero_factura}.xml"

    ElementTree(raiz).write(
        ruta,
        encoding="utf-8",
        xml_declaration=True,
        short_empty_elements=False,
    )

    return str(ruta)
