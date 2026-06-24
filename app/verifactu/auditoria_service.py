from app.models.factura import Factura
from app.models.verifactu_registro import VeriFactuRegistro

from app.verifactu.logger_service import log_verifactu
from app.verifactu.hash_service import generar_huella_aeat


def recalcular_cadena_hash(db):
    facturas = (
        db.query(Factura)
        .order_by(Factura.fecha.asc(), Factura.id.asc())
        .all()
    )

    hash_anterior = ""

    actualizadas = 0

    for factura in facturas:
        tipo_factura = (
            "R1"
            if factura.tipo_factura == "rectificativa"
            else "F1"
        )

        fecha_expedicion = factura.fecha.strftime("%d-%m-%Y")

        cuota_total = f"{float(factura.iva):.2f}"
        importe_total = f"{float(factura.total):.2f}"

        nuevo_hash = generar_huella_aeat(
            id_emisor="B21840988",
            num_serie=factura.numero_factura,
            fecha_expedicion=fecha_expedicion,
            tipo_factura=tipo_factura,
            cuota_total=cuota_total,
            importe_total=importe_total,
            huella_anterior=hash_anterior,
            fecha_hora_huso=factura.fecha_hora_huso_gen_registro
        )

        factura.hash_anterior = hash_anterior
        factura.hash_actual = nuevo_hash

        registro = (
            db.query(VeriFactuRegistro)
            .filter(VeriFactuRegistro.factura_id == factura.id)
            .first()
        )

        if registro:
            registro.hash_anterior = hash_anterior
            registro.hash_actual = nuevo_hash

        hash_anterior = nuevo_hash
        actualizadas += 1

    db.commit()

    log_verifactu(
        f"Cadena hash recalculada. Facturas actualizadas: {actualizadas}"
    )

    return {
        "ok": True,
        "facturas_actualizadas": actualizadas
    }

def verificar_cadena_hash(db):

    facturas = (
        db.query(Factura)
        .order_by(Factura.fecha.asc(), Factura.id.asc())
        .all()
    )

    errores = []

    hash_anterior_esperado = ""

    for factura in facturas:

        if (factura.hash_anterior or "") != hash_anterior_esperado:

            errores.append({
                "factura_id": factura.id,
                "numero_factura": factura.numero_factura,
                "campo": "hash_anterior",
                "esperado": hash_anterior_esperado,
                "encontrado": factura.hash_anterior
            })

        tipo_factura = "R1" if factura.tipo_factura == "rectificativa" else "F1"

        fecha_expedicion = factura.fecha.strftime("%d-%m-%Y")

        cuota_total = f"{float(factura.iva):.2f}"
        importe_total = f"{float(factura.total):.2f}"

        hash_recalculado = generar_huella_aeat(
            id_emisor="B21840988",
            num_serie=factura.numero_factura,
            fecha_expedicion=fecha_expedicion,
            tipo_factura=tipo_factura,
            cuota_total=cuota_total,
            importe_total=importe_total,
            huella_anterior=factura.hash_anterior or "",
            fecha_hora_huso=factura.fecha_hora_huso_gen_registro
        )

        if factura.hash_actual != hash_recalculado:

            errores.append({
                "factura_id": factura.id,
                "numero_factura": factura.numero_factura,
                "campo": "hash_actual",
                "esperado": hash_recalculado,
                "encontrado": factura.hash_actual
            })

        hash_anterior_esperado = factura.hash_actual or ""
    primer_hash = None
    ultimo_hash = None

    if facturas:
        primer_hash = facturas[0].hash_actual
        ultimo_hash = facturas[-1].hash_actual
    return {
        "ok": len(errores) == 0,
        "cadena_valida": len(errores) == 0,
        "facturas_verificadas": len(facturas),

        "errores": errores,
        "errores_detectados": len(errores),

        "primer_hash": primer_hash,
        "ultimo_hash": ultimo_hash
    }