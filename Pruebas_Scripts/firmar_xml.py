from app.verifactu.firma_service import firmar_xml_real

resultado = firmar_xml_real(
    "app/verifactu/storage/xml/R2026-000002.xml"
)

print(resultado)