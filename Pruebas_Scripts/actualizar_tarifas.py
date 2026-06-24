from app.database import SessionLocal
from app.models.tarifa_model import Tarifa

db = SessionLocal()

try:
    # Actualizar veterinario
    veterinario = (
        db.query(Tarifa)
        .filter(Tarifa.concepto == "servicio", Tarifa.tipo == "veterinario")
        .first()
    )

    if veterinario:
        veterinario.precio = 20
    else:
        db.add(Tarifa(concepto="servicio", tipo="veterinario", precio=20, activo=True))

    # Insertar extras
    extras = [
        ("extra", "lavado", 15),
        ("extra", "pienso", 10),
        ("extra", "peluqueria", 25),
    ]

    for concepto, tipo, precio in extras:
        existe = (
            db.query(Tarifa)
            .filter(Tarifa.concepto == concepto, Tarifa.tipo == tipo)
            .first()
        )

        if not existe:
            db.add(Tarifa(concepto=concepto, tipo=tipo, precio=precio, activo=True))

    db.commit()
    print("Tarifas actualizadas correctamente")

finally:
    db.close()