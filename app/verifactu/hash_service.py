# app/verifactu/hash_service.py

import hashlib


def obtener_ultimo_hash(db):
    from app.models.factura import Factura

    ultima_factura = (
        db.query(Factura)
        .filter(Factura.hash_actual.isnot(None))
        .order_by(Factura.id.desc())
        .first()
    )

    if not ultima_factura:
        return ""

    return ultima_factura.hash_actual

def formatear_importe_hash(valor):
    return str(float(valor))




def generar_huella_aeat(
    id_emisor,
    num_serie,
    fecha_expedicion,
    tipo_factura,
    cuota_total,
    importe_total,
    huella_anterior,
    fecha_hora_huso
):
    cadena = (
        f"IDEmisorFactura={id_emisor}"
        f"&NumSerieFactura={num_serie}"
        f"&FechaExpedicionFactura={fecha_expedicion}"
        f"&TipoFactura={tipo_factura}"
        f"&CuotaTotal={cuota_total}"
        f"&ImporteTotal={importe_total}"
        f"&Huella={huella_anterior}"
        f"&FechaHoraHusoGenRegistro={fecha_hora_huso}"
    )

    return hashlib.sha256(cadena.encode("utf-8")).hexdigest().upper()