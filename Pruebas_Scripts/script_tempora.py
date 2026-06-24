from app.verifactu.firma_service import firmar_xml_real

resultado = firmar_xml_real(
    "app/verifactu/storage/xml/2026-000001.xml"
)

print(resultado)