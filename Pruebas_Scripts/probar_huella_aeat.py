from app.verifactu.hash_service import generar_huella_aeat

huella = generar_huella_aeat(
    id_emisor="B21840988",
    num_serie="2026-000009",
    fecha_expedicion="04-06-2026",
    tipo_factura="F1",
    cuota_total="24.30",
    importe_total="140.00",
    huella_anterior="18be61e681fac779b02bf132cb937843c1af97f93bb426e899f89328db2617d1",
    fecha_hora_huso="2026-06-04T20:38:37+02:00"
)

print(huella)