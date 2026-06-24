from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import tempfile
from app.database import get_db
import os
from app.models.clientes import Cliente
from app.models.mascotas import Mascota
from app.models.residencias import Residencia
from app.models.estancia import Estancia

from app.schemas.clientes import ClienteCreate, ClienteUpdate, ClienteOut
from app.pdf.clientes_pdf import generar_pdf_cliente

from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from typing import Optional
from sqlalchemy import or_


templates = Jinja2Templates(
    directory="app/templates"
)


router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)




def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()






@router.get("/{cliente_id}/mascotas")
def obtener_mascotas_cliente(cliente_id: int, db: Session = Depends(get_db)):
    mascotas = db.query(Mascota).filter(Mascota.cliente_id == cliente_id).all()

    return mascotas

@router.post("/", response_model=ClienteOut)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    nuevo_cliente = Cliente(**cliente.model_dump())

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return nuevo_cliente


@router.get("/", response_model=list[ClienteOut])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).all()


@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return cliente


@router.put("/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(
    cliente_id: int,
    datos_cliente: ClienteUpdate,
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    for campo, valor in datos_cliente.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)

    return cliente

@router.get("/{cliente_id}/ficha")
def obtener_ficha_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    mascotas = db.query(Mascota).filter(Mascota.cliente_id == cliente_id).all()

    return {
        "cliente": cliente,
        "mascotas": mascotas
    }

@router.delete("/{cliente_id}")
def borrar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(cliente)
    db.commit()

    return {"mensaje": "Cliente eliminado correctamente"}


@router.get("/{cliente_id}/pdf")
def pdf_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    mascotas = db.query(Mascota).filter(Mascota.cliente_id == cliente_id).all()

    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"cliente_{cliente_id}.pdf")

    generar_pdf_cliente(
        cliente=cliente,
        mascotas=mascotas,
        output_path=output_path
    )

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename=f"cliente_{cliente_id}.pdf"
    )
@router.get("/{cliente_id}/resumen")
def obtener_resumen_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return {
        "id": cliente.id,
        "nombre": cliente.nombre,
        "apellidos": cliente.apellidos,
        "dni": cliente.dni,
        "telefono": cliente.telefono,
        "email": cliente.email,
        "direccion": cliente.direccion,
    }
@router.get("/{cliente_id}/ultimas-estancias")
def ultimas_estancias_cliente(cliente_id: int, db: Session = Depends(get_db)):
    estancias = (
        db.query(Estancia)
        .filter(Estancia.cliente_id == cliente_id)
        .order_by(Estancia.fecha_entrada.desc())
        .limit(3)
        .all()
    )

    return [
        {
            "fecha_entrada": str(e.fecha_entrada),
            "fecha_salida": str(e.fecha_salida),
            "habitacion": e.habitacion or "",
            "mascota": e.mascota.nombre if getattr(e, "mascota", None) else "",
            "tipo_precio_dia": e.tipo_precio_dia,
            "precio_dia": float(e.precio_dia or 0),
            "num_dias": getattr(e, "num_dias", None),
            "extras": e.extras or "",
            "importe_extras": float(e.importe_extras or 0),
            "camaras": e.camaras,
            "veterinario": e.veterinario,
            "transporte": e.transporte,
            "total": float(e.total or 0),
            "pagado": e.pagado,
        }
        for e in estancias
    ]
@router.get("/{cliente_id}/resumen-estancias")
def resumen_estancias_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    estancias = db.query(Estancia).filter(
        Estancia.cliente_id == cliente_id
    ).all()

    total_estancias = len(estancias)

    total_gastado = sum(
        float(e.total or 0)
        for e in estancias
    )

    ticket_medio = total_gastado / total_estancias if total_estancias else 0

    primera_estancia = (
        db.query(Estancia)
        .filter(Estancia.cliente_id == cliente_id)
        .order_by(Estancia.fecha_entrada.asc())
        .first()
    )
    if total_estancias >= 50 or total_gastado >= 5000:
        nivel = "💎 Premium"
    elif total_estancias >= 20 or total_gastado >= 2500:
        nivel = "🥇 Oro"
    elif total_estancias >= 10 or total_gastado >= 1000:
        nivel = "🥈 Plata"
    elif total_estancias >= 5 or total_gastado >= 500:
        nivel = "🥉 Bronce"
    else:
        nivel = "🐾 Nuevo"

    return {
        "total_estancias": total_estancias,
        "total_gastado": round(total_gastado, 2),
        "ticket_medio": round(ticket_medio, 2),
        "cliente_desde": (primera_estancia.fecha_entrada.strftime("%d/%m/%Y")
            if primera_estancia else None
        ),
        "nivel": nivel,
    }