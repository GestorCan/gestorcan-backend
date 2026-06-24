from app.models.verifactu_registro import VeriFactuRegistro

from app.verifactu.constants import (
    ESTADO_PENDIENTE,
    ESTADO_ERROR,ESTADO_FIRMADO

)

from app.verifactu.registro_service import (
    enviar_registro_a_aeat
)

from app.verifactu.logger_service import (
    log_verifactu
)


def procesar_registros_pendientes(db):

    pendientes = (
        db.query(VeriFactuRegistro)
        .filter(
            VeriFactuRegistro.estado == ESTADO_FIRMADO,
            VeriFactuRegistro.enviado == False
        )
        .all()
    )

    enviados = 0
    errores = 0

    for registro in pendientes:

        try:
            enviar_registro_a_aeat(db, registro)

            enviados += 1

            log_verifactu(
                f"Registro {registro.id} procesado automáticamente"
            )

        except Exception as e:
            registro.estado = ESTADO_ERROR
            registro.respuesta_aeat = str(e)

            db.commit()

            errores += 1

            log_verifactu(
                f"ERROR enviando registro {registro.id}: {str(e)}"
            )

    return {
        "total_pendientes": len(pendientes),
        "enviados": enviados,
        "errores": errores
    }