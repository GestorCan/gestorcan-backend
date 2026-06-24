from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.verifactu_registro import VeriFactuRegistro
from app.verifactu.registro_service import (
    enviar_registro_a_aeat
)


from fastapi.responses import FileResponse
import os
from app.verifactu.constants import (
    ESTADO_PENDIENTE,
    ESTADO_GENERADO,
    ESTADO_SIMULADO,
    ESTADO_ACEPTADO,
    ESTADO_RECHAZADO,
    ESTADO_ERROR,
    ESTADO_FIRMADO
)

from app.models.factura import Factura
from app.models.verifactu_registro import VeriFactuRegistro
from app.verifactu.registro_service import preparar_registro_verifactu
from app.verifactu.envio_service import (
    procesar_registros_pendientes
)

from app.verifactu.registro_service import (
    firmar_registro_verifactu
)
from app.verifactu.auditoria_service import recalcular_cadena_hash
from app.verifactu.auditoria_service import (
    recalcular_cadena_hash,
    verificar_cadena_hash
)
from fastapi import Request
from fastapi.templating import Jinja2Templates


router = APIRouter()


templates = Jinja2Templates(directory="app/templates")



@router.get("/signed/{registro_id}")
def descargar_signed_xml(
    registro_id: int,
    db: Session = Depends(get_db)
):

    registro = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.id == registro_id)
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=404,
            detail="Registro no encontrado"
        )

    if not registro.signed_xml_path:
        raise HTTPException(
            status_code=404,
            detail="XML firmado no disponible"
        )

    if not os.path.exists(registro.signed_xml_path):
        raise HTTPException(
            status_code=404,
            detail="Archivo firmado no encontrado"
        )

    return FileResponse(
        registro.signed_xml_path,
        media_type="application/xml",
        filename=os.path.basename(
            registro.signed_xml_path
        )
    )





@router.post("/firmar/{registro_id}")
def firmar_registro(registro_id: int, db: Session = Depends(get_db)):

    registro = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.id == registro_id)
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=404,
            detail="Registro VeriFactu no encontrado"
        )

    try:

        registro = firmar_registro_verifactu(
            db,
            registro
        )

        return {
            "ok": True,
            "registro_id": registro.id,
            "estado": registro.estado,
            "signed_xml_path": registro.signed_xml_path
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/procesar-pendientes")
def procesar_pendientes(db: Session = Depends(get_db)):

    resultado = procesar_registros_pendientes(db)

    return resultado


@router.post("/reconstruir-registros")
def reconstruir_registros(db: Session = Depends(get_db)):

    facturas = (
        db.query(Factura)
        .order_by(Factura.id.asc())
        .all()
    )

    creados = 0

    for factura in facturas:

        existente = (
            db.query(VeriFactuRegistro)
            .filter(
                VeriFactuRegistro.factura_id == factura.id
            )
            .first()
        )

        if existente:
            continue

        preparar_registro_verifactu(db, factura)

        creados += 1

    db.commit()

    return {
        "ok": True,
        "registros_creados": creados
    }




@router.post("/enviar/{registro_id}")
def enviar_registro(registro_id: int, db: Session = Depends(get_db)):

    registro = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.id == registro_id)
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=404,
            detail="Registro VeriFactu no encontrado"
        )

    try:

        resultado = enviar_registro_a_aeat(
            db,
            registro
        )

        return {
            "ok": True,
            "registro_id": resultado.id,
            "estado": resultado.estado,
            "fecha_envio": resultado.fecha_envio,
            "respuesta": resultado.respuesta_aeat
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/registros")
def listar_registros(db: Session = Depends(get_db)):

    registros = db.query(VeriFactuRegistro).all()

    return [
        {
            "id": r.id,
            "factura_id": r.factura_id,
            "estado": r.estado,
            "enviado": r.enviado,
            "xml_path": r.xml_path,
            "qr_path": r.qr_path,
        }
        for r in registros
    ]

@router.get("/xml/{registro_id}")
def descargar_xml(registro_id: int, db: Session = Depends(get_db)):

    registro = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.id == registro_id)
        .first()
    )

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    if not registro.xml_path:
        raise HTTPException(status_code=404, detail="XML no disponible")

    if not os.path.exists(registro.xml_path):
        raise HTTPException(status_code=404, detail="Archivo XML no encontrado")

    return FileResponse(
        registro.xml_path,
        media_type="application/xml",
        filename=os.path.basename(registro.xml_path)
    )

@router.get("/qr/{registro_id}")
def descargar_qr(registro_id: int, db: Session = Depends(get_db)):

    registro = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.id == registro_id)
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=404,
            detail="Registro no encontrado"
        )

    if not registro.qr_path:
        raise HTTPException(
            status_code=404,
            detail="QR no disponible"
        )

    if not os.path.exists(registro.qr_path):
        raise HTTPException(
            status_code=404,
            detail="Archivo QR no encontrado"
        )

    return FileResponse(
        registro.qr_path,
        media_type="image/png",
        filename=os.path.basename(registro.qr_path)
    )
@router.get("/dashboard")
def dashboard_verifactu(
    request: Request,
    db: Session = Depends(get_db)
):

    total_registros = db.query(VeriFactuRegistro).count()

    pendientes = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.estado == ESTADO_PENDIENTE)
        .count()
    )

    firmados = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.estado == ESTADO_FIRMADO)
        .count()
    )

    aceptados = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.estado == ESTADO_ACEPTADO)
        .count()
    )

    errores = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.estado == ESTADO_ERROR)
        .count()
    )

    enviados = (
        db.query(VeriFactuRegistro)
        .filter(VeriFactuRegistro.enviado == True)
        .count()
    )

    registros = (
        db.query(VeriFactuRegistro)
        .order_by(VeriFactuRegistro.id.desc())
        .all()
    )

    facturas = (
        db.query(Factura)
        .order_by(Factura.fecha.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="fiscal/verifactu/dashboard.html",
        context={
            "total_registros": total_registros,
            "pendientes": pendientes,
            "firmados": firmados,
            "aceptados": aceptados,
            "errores": errores,
            "enviados": enviados,
            "registros": registros,
            "facturas": facturas
        }
    )
