from app.database import SessionLocal


from app.database import SessionLocal
from sqlalchemy import text


def obtener_albaranes(cliente=None, fecha=None):
    db = SessionLocal()

    try:
        query = """
            SELECT 
                e.id,
                c.nombre AS cliente,
                m.nombre AS mascota,
                e.fecha_entrada,
                e.fecha_salida,
                e.total,
                e.ruta_albaran_pdf
            FROM estancias e
            JOIN clientes c ON e.cliente_id = c.id
            JOIN mascotas m ON e.mascota_id = m.id
            WHERE 1 = 1
        """

        params = {}

        if cliente:
            query += " AND c.nombre LIKE :cliente"
            params["cliente"] = f"%{cliente}%"

        if fecha:
            query += """
                AND e.fecha_entrada <= :fecha
                AND e.fecha_salida >= :fecha
            """
            params["fecha"] = fecha

        query += " ORDER BY e.fecha_entrada DESC"

        result = db.execute(text(query), params)

        return [dict(row._mapping) for row in result.fetchall()]

    finally:
        db.close()