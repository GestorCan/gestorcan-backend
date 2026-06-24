from pathlib import Path

CARPETA = Path(r"C:\Users\cualq\gestorcan-backend\media\facturas\2026")

for archivo in CARPETA.glob("Factura_*.pdf"):

    numero = archivo.stem.split("_")[-1]

    nuevo_archivo = CARPETA / f"2026-{numero}.pdf"

    if nuevo_archivo.exists():
        print(f"DUPLICADO: {archivo.name} -> {nuevo_archivo.name}")
        continue

    print(f"{archivo.name} -> {nuevo_archivo.name}")

    archivo.rename(nuevo_archivo)