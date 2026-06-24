from pathlib import Path
from lxml import etree


def validar_xml(xml_path):

    xsd_path = Path(
        "FICHEROS_AEAT/SuministroLR.xsd"
    )

    xml_doc = etree.parse(xml_path)

    xsd_doc = etree.parse(
        str(xsd_path)
    )

    schema = etree.XMLSchema(
        xsd_doc
    )

    valido = schema.validate(
        xml_doc
    )

    if valido:
        print(
            "XML VALIDO"
        )
        return True

    print(
        "XML INVALIDO"
    )

    for error in schema.error_log:
        print(error.message)

    return False