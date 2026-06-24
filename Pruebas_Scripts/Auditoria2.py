import hashlib

hash_bd = "d309493e7477231ac28190557ac7343f9ea91a9c448cee675d9a53e837c7392c"
hash_anterior = "da0115fdeceb8fb57942ad8ca6c15713ad675d3004b0f512c9b3afa776854642"

variantes = {
    "actual": "2026-000022|2026|2026-06-04|13|21|309.92|65.08|375.00|" + hash_anterior,

    "fecha_dd_mm_yyyy": "2026-000022|2026|04-06-2026|13|21|309.92|65.08|375.00|" + hash_anterior,

    "total_1_decimal": "2026-000022|2026|2026-06-04|13|21|309.92|65.08|375.0|" + hash_anterior,

    "sin_estancia": "2026-000022|2026|2026-06-04|13|None|309.92|65.08|375.00|" + hash_anterior,

    "fecha_datetime": "2026-000022|2026|2026-06-04 00:00:00|13|21|309.92|65.08|375.00|" + hash_anterior,
}

for nombre, cadena in variantes.items():
    h = hashlib.sha256(cadena.encode("utf-8")).hexdigest()

    print(nombre)
    print(h)
    print("COINCIDE:", h == hash_bd)
    print()