from app.database import SessionLocal
from app.models.tarifa_model import Tarifa

tarifas_base = [
    {"concepto": "estancia_dia", "tipo": "normal", "precio": 20},
    {"concepto": "estancia_dia", "tipo": "agresivo_perros", "precio": 25},
    {"concepto": "estancia_dia", "tipo": "agresivo_personas", "precio": 30},
    {"concepto": "estancia_dia", "tipo": "hembra_embarazada", "precio": 35},

    {"concepto": "servicio", "tipo": "camaras", "precio": 5},
    {"concepto": "servicio", "tipo": "veterinario", "precio": 50},

    {"concepto": "transporte_km", "tipo": "km", "precio": 0.50},
    {"concepto": "extra", "tipo": "lavado", "precio": 15},
    {"concepto": "extra", "tipo": "pienso", "precio": 10},
    {"concepto": "extra", "tipo": "peluqueria", "precio": 25},
]

db = SessionLocal()

try:
    for t in tarifas_base:
        existe = (
            db.query(Tarifa)
            .filter(
                Tarifa.concepto == t["concepto"],
                Tarifa.tipo == t["tipo"]
            )
            .first()
        )

        if not existe:
            db.add(Tarifa(**t))

    db.commit()
    print("Tarifas insertadas correctamente")

finally:
    db.close()