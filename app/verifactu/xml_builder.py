# app/verifactu/xml_builder.py

import os
from pathlib import Path
import xml.etree.ElementTree as ET


from app.verifactu.config import XML_DIR

XML_DIR.mkdir(parents=True, exist_ok=True)


def generar_xml_factura(factura):

    root = ET.Element("Factura")

    ET.SubElement(root, "NumeroFactura").text = str(factura.numero_factura)

    ET.SubElement(root, "Serie").text = str(factura.serie)

    ET.SubElement(root, "Fecha").text = str(factura.fecha)

    ET.SubElement(root, "ClienteID").text = str(factura.cliente_id)

    ET.SubElement(root, "BaseImponible").text = str(factura.base_imponible)

    ET.SubElement(root, "IVA").text = str(factura.iva)

    ET.SubElement(root, "Total").text = str(factura.total)

    ET.SubElement(root, "HashAnterior").text = str(
        factura.hash_anterior or ""
    )

    ET.SubElement(root, "HashActual").text = str(
        factura.hash_actual
    )

    tree = ET.ElementTree(root)

    output_path = (
        XML_DIR /
        f"factura_{factura.numero_factura}.xml"
    )

    tree.write(
        output_path,
        encoding="utf-8",
        xml_declaration=True
    )

    return str(output_path)