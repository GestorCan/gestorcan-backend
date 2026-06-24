from app.models.verifactu_registro import VeriFactuRegistro
from app.verifactu.constants import (
    ESTADO_FIRMADO,
    ESTADO_ACEPTADO,
    ESTADO_ERROR
)

def obtener_dashboard_verifactu(db):

    total = db.query(
        VeriFactuRegistro
    ).count()

    firmados = (
        db.query(VeriFactuRegistro)
        .filter(
            VeriFactuRegistro.estado == ESTADO_FIRMADO
        )
        .count()
    )

    aceptados = (
        db.query(VeriFactuRegistro)
        .filter(
            VeriFactuRegistro.estado == ESTADO_ACEPTADO
        )
        .count()
    )

    errores = (
        db.query(VeriFactuRegistro)
        .filter(
            VeriFactuRegistro.estado == ESTADO_ERROR
        )
        .count()
    )

    return {
        "total": total,
        "firmados": firmados,
        "aceptados": aceptados,
        "errores": errores
    }