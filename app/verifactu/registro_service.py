from app.models.verifactu_registro import VeriFactuRegistro
from app.verifactu.hash_service import obtener_ultimo_hash
from app.verifactu.qr_service import generar_qr_factura
from app.verifactu.xml_builder import generar_xml_factura
from app.verifactu.aeat_client import enviar_registro_verifactu
from app.verifactu.constants import (
    ESTADO_PENDIENTE,
    ESTADO_FIRMADO,
    TIPO_ALTA
)
from app.verifactu.logger_service import log_verifactu
from app.verifactu.firma_service import firmar_xml_simulado, firmar_xml_real
from app.verifactu.constants import ESTADO_FIRMADO
from app.models.residencias import Residencia
from app.models.factura import Factura
from app.verifactu.xml_builder_aeat import generar_xml_aeat

import os

from datetime import datetime
from zoneinfo import ZoneInfo

from app.verifactu.hash_service import obtener_ultimo_hash, generar_huella_aeat


from app.verifactu.settings import firma_real_activada
from app.verifactu.firma_service import firmar_xml_simulado, firmar_xml_real
from app.verifactu.constants import (
    ESTADO_PENDIENTE,
    ESTADO_FIRMADO,
    ESTADO_ACEPTADO,
    ESTADO_ERROR,
    TIPO_ALTA
)

def firmar_xml_verifactu(xml_path: str):
    if firma_real_activada():
        return firmar_xml_real(xml_path)

    return firmar_xml_simulado(xml_path)



def firmar_registro_verifactu(db, registro):

    if not registro.xml_path:
        raise Exception("El registro no tiene XML generado")

    if registro.signed_xml_path:
        raise Exception("El registro ya está firmado")

    firma_resultado = firmar_xml_verifactu(registro.xml_path)

    registro.signed_xml_path = firma_resultado["signed_path"]
    registro.estado = ESTADO_FIRMADO

    db.commit()
    db.refresh(registro)

    log_verifactu(
        f"Registro {registro.id} firmado correctamente"
    )

    return registro



def preparar_registro_verifactu(db, factura):
    hash_anterior = obtener_ultimo_hash(db)

    residencia = (
        db.query(Residencia)
        .filter(Residencia.activa == True)
        .first()
    )

    factura_anterior = None

    if hash_anterior:
        factura_anterior = (
            db.query(Factura)
            .filter(Factura.hash_actual == hash_anterior)
            .first()
        )

    fecha_hora_huso = datetime.now(
        ZoneInfo("Europe/Madrid")
    ).isoformat(timespec="seconds")

    tipo_factura = "R1" if factura.tipo_factura == "rectificativa" else "F1"

    fecha_expedicion = factura.fecha.strftime("%d-%m-%Y")

    cuota_total = f"{float(factura.iva):.2f}"
    importe_total = f"{float(factura.total):.2f}"

    hash_actual = generar_huella_aeat(
        id_emisor=residencia.cif,
        num_serie=factura.numero_factura,
        fecha_expedicion=fecha_expedicion,
        tipo_factura=tipo_factura,
        cuota_total=cuota_total,
        importe_total=importe_total,
        huella_anterior=hash_anterior,
        fecha_hora_huso=fecha_hora_huso
    )

    factura.hash_anterior = hash_anterior
    factura.hash_actual = hash_actual
    factura.fecha_hora_huso_gen_registro = fecha_hora_huso

    qr_path = generar_qr_factura(factura)
    factura.qr_path = qr_path

    xml_path = generar_xml_aeat(
        factura=factura,
        residencia=residencia,
        cliente=factura.cliente,
        factura_anterior=factura_anterior
    )

    firma_resultado = firmar_xml_verifactu(xml_path)

    signed_xml_path = firma_resultado["signed_path"]

    if factura.tipo_factura == "rectificativa":
        tipo_registro = "rectificativa"
    else:
        tipo_registro = TIPO_ALTA

    registro = VeriFactuRegistro(
        factura_id=factura.id,

        numero_factura=factura.numero_factura,
        tipo_factura=factura.tipo_factura,

        tipo_registro=tipo_registro,
        estado=ESTADO_FIRMADO,

        hash_anterior=hash_anterior,
        hash_actual=hash_actual,

        qr_path=qr_path,
        xml_path=xml_path,

        enviado=False,
        signed_xml_path=signed_xml_path
    )

    db.add(registro)
    db.flush()

    log_verifactu(
        f"Registro VeriFactu creado para factura {factura.numero_factura}"
    )

    return registro




def enviar_registro_a_aeat(db, registro):
    if registro.enviado:
        raise Exception("Este registro VeriFactu ya fue enviado")
    if registro.estado != ESTADO_FIRMADO:
        raise Exception("El registro debe estar firmado antes de enviarse")

    respuesta = enviar_registro_verifactu(registro.signed_xml_path)

    registro.enviado = respuesta["ok"]

    if respuesta["ok"]:
        registro.estado = respuesta.get("estado") or ESTADO_ACEPTADO
    else:
        registro.estado = ESTADO_ERROR
    registro.fecha_envio = respuesta["fecha_envio"]
    registro.respuesta_aeat = respuesta["respuesta"]

    registro.csv_aeat = respuesta.get("csv")
    registro.estado_aeat = respuesta.get("estado_registro")
    registro.codigo_error_aeat = respuesta.get("codigo_error")
    registro.descripcion_error_aeat = respuesta.get("descripcion_error")
    registro.timestamp_presentacion = respuesta.get("timestamp_presentacion")

    db.commit()
    db.refresh(registro)
    log_verifactu(
        f"Registro {registro.id} enviado a AEAT. Estado: {registro.estado}"
    )
    return registro