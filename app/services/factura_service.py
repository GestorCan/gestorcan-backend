# app/services/factura_service.py

from datetime import date

from sqlalchemy.orm import Session

from app.models.factura import Factura
from app.models.estancia import Estancia

from app.repositories.factura_repository import generar_numero_factura
from app.pdf.factura_pdf import generar_pdf_factura
from app.verifactu.registro_service import preparar_registro_verifactu
from app.verifactu.qr_service import generar_qr_factura
from app.models.verifactu_registro import VeriFactuRegistro
from app.repositories.factura_repository import listar_facturas, obtener_factura_por_id
from app.services.pdf_rectificativa import generar_pdf_rectificativa
from app.models.residencias import Residencia


IVA_PORCENTAJE = 0.21


def crear_factura_desde_estancia(db: Session, estancia_id: int):

    estancia = (
        db.query(Estancia)
        .filter(Estancia.id == estancia_id)
        .first()
    )

    if not estancia:
        raise Exception("Estancia no encontrada")

    if estancia.facturado:
        raise Exception("La estancia ya está facturada")

    numero_factura, serie = generar_numero_factura(db)

    # IMPORTANTE:
    # Los importes ya incluyen IVA

    total = float(estancia.total)

    base_imponible = round(total / (1 + IVA_PORCENTAJE), 2)

    iva = round(total - base_imponible, 2)

    factura = Factura(
        numero_factura=numero_factura,
        serie=serie,
        fecha=date.today(),

        cliente_id=estancia.cliente_id,
        estancia_id=estancia.id,

        base_imponible=base_imponible,
        iva=iva,
        total=total,

        estado_pago="pendiente",
        tipo_factura="ordinaria"
    )

    estancia.facturado = True
    db.add(factura)
    db.flush()

    from app.verifactu.settings import verifactu_activado

    if verifactu_activado():
        preparar_registro_verifactu(db, factura)

    pdf_path = generar_pdf_factura(
        factura=factura,
        estancia=estancia,
        cliente=estancia.cliente,
        mascota=estancia.mascota
    )

    factura.pdf_path = pdf_path
    estancia.facturado = True

    db.commit()
    db.refresh(factura)

    return factura
def listar_facturas_con_verifactu(db):
    facturas = listar_facturas(db)

    resultado = []

    for factura in facturas:
        registro = (
            db.query(VeriFactuRegistro)
            .filter(VeriFactuRegistro.factura_id == factura.id)
            .first()
        )

        resultado.append({
            "id": factura.id,
            "numero_factura": factura.numero_factura,
            "serie": factura.serie,
            "fecha": factura.fecha,
            "cliente_id": factura.cliente_id,
            "estancia_id": factura.estancia_id,
            "base_imponible": float(factura.base_imponible),
            "iva": float(factura.iva),
            "total": float(factura.total),
            "estado_pago": factura.estado_pago,
            "pdf_path": factura.pdf_path,
            "qr_path": factura.qr_path,
            "hash_actual": factura.hash_actual,
            "verifactu": {
                "estado": registro.estado if registro else None,
                "enviado": registro.enviado if registro else False,
                "xml_path": registro.xml_path if registro else None,
                "fecha_envio": registro.fecha_envio if registro else None,
            }
        })

    return resultado


def obtener_detalle_factura(db, factura_id: int):
    factura = obtener_factura_por_id(db, factura_id)

    if not factura:
        raise Exception("Factura no encontrada")

    registro = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.factura_id == factura.id)
        .first()
    )

    return {
        "id": factura.id,
        "numero_factura": factura.numero_factura,
        "serie": factura.serie,
        "fecha": factura.fecha,
        "cliente_id": factura.cliente_id,
        "estancia_id": factura.estancia_id,
        "base_imponible": float(factura.base_imponible),
        "iva": float(factura.iva),
        "total": float(factura.total),
        "estado_pago": factura.estado_pago,
        "pdf_path": factura.pdf_path,
        "qr_path": factura.qr_path,
        "hash_anterior": factura.hash_anterior,
        "hash_actual": factura.hash_actual,
        "verifactu": {
            "registro_id": registro.id if registro else None,
            "estado": registro.estado if registro else None,
            "enviado": registro.enviado if registro else False,
            "xml_path": registro.xml_path if registro else None,
            "qr_path": registro.qr_path if registro else None,
            "fecha_envio": registro.fecha_envio if registro else None,
            "respuesta_aeat": registro.respuesta_aeat if registro else None,
        }
    }

def generar_numero_rectificativa(db: Session):

    year = date.today().year

    serie = f"R{year}"

    ultima = (
        db.query(Factura)
        .filter(Factura.serie == serie)
        .order_by(Factura.id.desc())
        .first()
    )

    if ultima:
        ultimo_numero = int(
            ultima.numero_factura.split("-")[-1]
        )

        siguiente = ultimo_numero + 1

    else:
        siguiente = 1

    numero_factura = (
        f"{serie}-{str(siguiente).zfill(6)}"
    )

    return numero_factura, serie








def crear_factura_rectificativa(
    db: Session,
    factura_original_id: int,
    motivo: str,
    total_rectificado: float
):
    factura_original = (
        db.query(Factura)
        .filter(Factura.id == factura_original_id)
        .first()
    )

    if not factura_original:
        raise Exception("Factura original no encontrada")

    numero_factura, serie = generar_numero_rectificativa(db)

    total = float(total_rectificado)

    base_imponible = round(
        total / (1 + IVA_PORCENTAJE),
        2
    )

    iva = round(
        total - base_imponible,
        2
    )

    rectificativa = Factura(
        numero_factura=numero_factura,
        serie=serie,
        fecha=date.today(),

        cliente_id=factura_original.cliente_id,
        estancia_id=None,

        base_imponible=base_imponible,
        iva=iva,
        total=total,

        estado_pago="pendiente",

        tipo_factura="rectificativa",
        factura_rectificada_id=factura_original.id,
        motivo_rectificacion=motivo,
        tipo_rectificativa="I",
        serie_rectificativa=serie
    )

    db.add(rectificativa)
    db.flush()

    preparar_registro_verifactu(db, rectificativa)

    residencia = (
        db.query(Residencia)
        .filter(Residencia.activa == True)
        .first()
    )

    pdf_path = generar_pdf_rectificativa(
        factura=rectificativa,
        factura_original=factura_original,
        cliente=factura_original.cliente,
        residencia=residencia
    )

    rectificativa.pdf_path = pdf_path

    db.commit()
    db.refresh(rectificativa)

    return rectificativa
