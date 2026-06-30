from pathlib import Path
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from app.models.estancia import Estancia
from app.models.mascotas import Mascota
from app.models.habitacion import Habitacion


GRUPOS = {
    "P": "Pequeños",
    "M": "Medianos",
    "G": "Grandes",
}


def grupo_habitacion(nombre):
    if not nombre:
        return None
    inicial = nombre.strip().upper()[0]
    return inicial if inicial in GRUPOS else None


def color_estado(pct):
    if pct >= 95:
        return colors.HexColor("#e74c3c")  # rojo
    if pct >= 80:
        return colors.HexColor("#f39c12")  # naranja
    return colors.HexColor("#2ecc71")      # verde


def texto_estado(pct):
    if pct >= 95:
        return "COMPLETO"
    if pct >= 80:
        return "ALTA"
    return "VENDER"


def dibujar_barra(c, x, y, ancho, alto, pct):
    c.setFillColor(colors.HexColor("#e9ecef"))
    c.roundRect(x, y, ancho, alto, 4, fill=1, stroke=0)

    relleno = ancho * min(pct, 100) / 100
    c.setFillColor(color_estado(pct))
    c.roundRect(x, y, relleno, alto, 4, fill=1, stroke=0)


def generar_informe_ocupacion_pdf(db) -> str:
    BASE_DIR = Path(__file__).resolve().parents[1]
    carpeta = BASE_DIR / "reports" / "autoreports"
    carpeta.mkdir(parents=True, exist_ok=True)

    hoy = date.today()
    archivo_pdf = carpeta / f"informe_ocupacion_{hoy}.pdf"

    habitaciones = db.query(Habitacion).filter(Habitacion.activa == True).all()

    capacidad = {"P": 0, "M": 0, "G": 0}

    for h in habitaciones:
        grupo = grupo_habitacion(h.nombre)
        if grupo:
            capacidad[grupo] += 1

    capacidad_total = sum(capacidad.values())

    datos = []

    for i in range(7):
        dia = hoy + timedelta(days=i + 1)

        estancias = db.query(Estancia).join(Mascota).filter(
            Estancia.fecha_entrada <= dia,
            Estancia.fecha_salida > dia
        ).all()

        entradas = db.query(Estancia).join(Mascota).filter(
            Estancia.fecha_entrada == dia
        ).all()

        salidas = db.query(Estancia).join(Mascota).filter(
            Estancia.fecha_salida == dia
        ).all()

        ocupadas = {"P": set(), "M": set(), "G": set()}

        for e in estancias:
            grupo = grupo_habitacion(e.habitacion)
            if grupo:
                ocupadas[grupo].add(e.habitacion)

        resumen = {}

        for g in ["P", "M", "G"]:
            occ = len(ocupadas[g])
            cap = capacidad[g]
            pct = round((occ / cap) * 100, 1) if cap else 0
            resumen[g] = {
                "ocupadas": occ,
                "capacidad": cap,
                "libres": max(cap - occ, 0),
                "pct": pct,
            }

        total_ocupadas = sum(resumen[g]["ocupadas"] for g in ["P", "M", "G"])
        pct_total = round((total_ocupadas / capacidad_total) * 100, 1) if capacidad_total else 0

        datos.append({
            "fecha": dia,
            "resumen": resumen,
            "total_ocupadas": total_ocupadas,
            "capacidad_total": capacidad_total,
            "libres_total": max(capacidad_total - total_ocupadas, 0),
            "pct_total": pct_total,
            "entradas": entradas,
            "salidas": salidas,
        })

    c = canvas.Canvas(str(archivo_pdf), pagesize=landscape(A4))
    width, height = landscape(A4)

    # CABECERA
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.rect(0, height - 55, width, 55, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(35, height - 35, "Informe comercial de ocupación")

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 35, height - 35, f"Generado: {hoy.strftime('%d/%m/%Y')}")

    # TARJETAS RESUMEN DEL PRIMER DÍA
    primer = datos[0]
    x = 35
    y = height - 120
    card_w = 180
    card_h = 70
    gap = 18

    for idx, g in enumerate(["P", "M", "G"]):
        r = primer["resumen"][g]
        pct = r["pct"]

        c.setFillColor(colors.white)
        c.roundRect(x + idx * (card_w + gap), y, card_w, card_h, 8, fill=1, stroke=1)

        c.setFillColor(color_estado(pct))
        c.roundRect(x + idx * (card_w + gap), y + card_h - 12, card_w, 12, 8, fill=1, stroke=0)

        c.setFillColor(colors.HexColor("#2c3e50"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + idx * (card_w + gap) + 12, y + 45, GRUPOS[g])

        c.setFont("Helvetica-Bold", 18)
        c.drawString(
            x + idx * (card_w + gap) + 12,
            y + 22,
            f"{r['ocupadas']}/{r['capacidad']}"
        )

        c.setFont("Helvetica", 10)
        c.drawRightString(
            x + idx * (card_w + gap) + card_w - 12,
            y + 25,
            f"Libres: {r['libres']} · {pct}%"
        )

    # TOTAL
    total_x = x + 3 * (card_w + gap)
    c.setFillColor(colors.white)
    c.roundRect(total_x, y, 190, card_h, 8, fill=1, stroke=1)

    c.setFillColor(color_estado(primer["pct_total"]))
    c.roundRect(total_x, y + card_h - 12, 190, 12, 8, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#2c3e50"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(total_x + 12, y + 45, "TOTAL RESIDENCIA")

    c.setFont("Helvetica-Bold", 18)
    c.drawString(total_x + 12, y + 22, f"{primer['total_ocupadas']}/{primer['capacidad_total']}")

    c.setFont("Helvetica", 10)
    c.drawRightString(total_x + 175, y + 25, f"{primer['pct_total']}%")

    # TABLA 7 DÍAS
    y = height - 170

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(35, y, "Previsión de ocupación por tamaño - próximos 7 días")

    y -= 25

    headers = ["Fecha", "Pequeños", "Medianos", "Grandes", "Total", "Estado"]
    col_x = [35, 115, 260, 405, 550, 700]

    c.setFont("Helvetica-Bold", 9)
    for h, cx in zip(headers, col_x):
        c.drawString(cx, y, h)

    y -= 12
    c.line(35, y, width - 35, y)
    y -= 18

    for fila in datos:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#2c3e50"))
        c.drawString(35, y + 5, fila["fecha"].strftime("%d/%m"))

        for idx, g in enumerate(["P", "M", "G"]):
            r = fila["resumen"][g]
            bx = col_x[idx + 1]
            dibujar_barra(c, bx, y, 85, 10, r["pct"])

            c.setFillColor(colors.HexColor("#2c3e50"))
            c.setFont("Helvetica", 8)
            c.drawString(bx + 92, y + 1, f"{r['ocupadas']}/{r['capacidad']}")

        dibujar_barra(c, col_x[4], y, 90, 10, fila["pct_total"])

        c.setFillColor(colors.HexColor("#2c3e50"))
        c.setFont("Helvetica", 8)
        c.drawString(col_x[4] + 98, y + 1, f"{fila['total_ocupadas']}/{fila['capacidad_total']}")

        c.setFillColor(color_estado(fila["pct_total"]))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(col_x[5], y + 1, texto_estado(fila["pct_total"]))

        y -= 28

    # PÁGINA 2 - OPERATIVA
    c.showPage()

    c.setFillColor(colors.HexColor("#2c3e50"))
    c.rect(0, height - 55, width, 55, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(35, height - 35, "Entradas y salidas previstas")

    y = height - 90

    for fila in datos:
        if y < 90:
            c.showPage()
            y = height - 60

        c.setFillColor(colors.HexColor("#2c3e50"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(35, y, fila["fecha"].strftime("%d/%m/%Y"))

        y -= 18

        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y, "Entradas")
        c.drawString(400, y, "Salidas")

        y -= 15

        max_lineas = max(len(fila["entradas"]), len(fila["salidas"]), 1)

        for i in range(max_lineas):
            c.setFont("Helvetica", 8)

            if i < len(fila["entradas"]):
                e = fila["entradas"][i]
                mascota = e.mascota.nombre if e.mascota else ""
                c.drawString(50, y, f"- {mascota} · Hab. {e.habitacion or '-'}")

            if i < len(fila["salidas"]):
                s = fila["salidas"][i]
                mascota = s.mascota.nombre if s.mascota else ""
                c.drawString(400, y, f"- {mascota} · Hab. {s.habitacion or '-'}")

            y -= 12

        y -= 12

    c.save()

    return str(archivo_pdf)