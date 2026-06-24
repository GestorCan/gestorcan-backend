import hashlib

from app.database import SessionLocal

from app.models.mascotas import Mascota
from app.models.clientes import Cliente
from app.models.estancia import Estancia
from app.models.factura import Factura


def cadena_hash_factura(factura, hash_anterior=""):
    return (
        f"{factura.numero_factura}|"
        f"{factura.serie}|"
        f"{factura.fecha}|"
        f"{factura.cliente_id}|"
        f"{factura.estancia_id}|"
        f"{factura.base_imponible}|"
        f"{factura.iva}|"
        f"{factura.total}|"
        f"{hash_anterior}"
    )


db = SessionLocal()

factura = (
    db.query(Factura)
    .filter(Factura.numero_factura == "2026-000022")
    .first()
)

cadena = cadena_hash_factura(factura, factura.hash_anterior or "")
hash_recalculado = hashlib.sha256(cadena.encode("utf-8")).hexdigest()

print("FACTURA:", factura.numero_factura)
print("CADENA:")
print(cadena)
print()
print("BD       :", factura.hash_actual)
print("CALCULADO:", hash_recalculado)
print("COINCIDE :", factura.hash_actual == hash_recalculado)

db.close()