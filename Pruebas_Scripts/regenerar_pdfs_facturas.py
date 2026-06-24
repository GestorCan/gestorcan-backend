import os

os.environ["DATABASE_URL"] = (
    "sqlite:///C:/Users/cualq/gestorcan-backend/gestorcan_local.db"
)

from app.database import SessionLocal
from app.models.factura import Factura
from app.models.estancia import Estancia
from app.models.clientes import Cliente
from app.models.mascotas import Mascota
from app.pdf.factura_pdf import generar_pdf_factura
db = SessionLocal()
print("DATABASE_URL:", os.environ.get("DATABASE_URL"))
try:
    factura = db.query(Factura).filter(Factura.id == 1043).first()

    if not factura:
        print("Factura no encontrada")
    else:
        estancia = db.query(Estancia).filter(
            Estancia.id == factura.estancia_id
        ).first()

        cliente = db.query(Cliente).filter(
            Cliente.id == estancia.cliente_id
        ).first()

        mascota = db.query(Mascota).filter(
            Mascota.id == estancia.mascota_id
        ).first()

        ruta_pdf = generar_pdf_factura(
            factura=factura,
            estancia=estancia,
            cliente=cliente,
            mascota=mascota
        )

        factura.pdf_path = str(ruta_pdf)
        db.commit()

        print(f"PDF generado: {ruta_pdf}")
        import os

        print("Ruta devuelta:", ruta_pdf)
        print("Ruta absoluta:", os.path.abspath(ruta_pdf))
        print("Existe:", os.path.exists(ruta_pdf))

except Exception as e:
    db.rollback()
    print(f"ERROR: {e}")

finally:
    db.close()