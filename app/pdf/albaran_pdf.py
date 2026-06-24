from fpdf import FPDF
from datetime import datetime
import os



def limpiar_texto_pdf(valor):
    if valor is None:
        return ""

    texto = str(valor)

    caracteres_problematicos = {
        "\u200b": "",   # espacio invisible
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
        "€": "EUR",
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }

    for malo, bueno in caracteres_problematicos.items():
        texto = texto.replace(malo, bueno)

    return texto.encode("latin-1", "ignore").decode("latin-1")


def caja(pdf, titulo):
    pdf.set_fill_color(245, 247, 250)  # gris muy suave
    pdf.set_draw_color(220, 220, 220)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, titulo, 0, 1)

    pdf.rect(pdf.get_x(), pdf.get_y(), 190, 0)  # línea fina

def linea(pdf):
    pdf.set_draw_color(200, 200, 200)  # gris suave
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

def campo(pdf, etiqueta, valor, ancho=95, salto=False):
    pdf.set_font("Arial", "B", 10)
    pdf.cell(28, 6, f"{etiqueta}:", 0, 0)

    pdf.set_font("Arial", "", 10)
    pdf.cell(
        ancho - 28,
        6,
        limpiar_texto_pdf(valor),
        0,
        1 if salto else 0
    )

def campo2(pdf, etiqueta, valor, ancho=95, salto=False):
    pdf.set_font("Arial", "B", 10)
    pdf.cell(32, 6, f"{etiqueta}:", 0, 0)

    pdf.set_font("Arial", "", 10)
    pdf.cell(
        ancho - 28,
        6,
        limpiar_texto_pdf(valor),
        0,
        1 if salto else 0
    )

class AlbaranPDF(FPDF):

    def header(self):
        self.image("static/logos/logo.png", x=10, y=8, w=14,)

        self.set_font("Arial", "B", 14)
        self.cell(0, 8, "ALBARÁN DE RESERVA", 0, 1, "R")
        self.ln(6)


def generar_pdf_albaran(estancia, output_path):
    from app.pdf.pdf_base import PDFBase

    pdf = PDFBase()
    pdf.add_page()

    # Cabecera profesional
    pdf.cabecera("ALBARÁN DE RESERVA", estancia.id)

    # ===== CLIENTE =====
    # ===== CLIENTE =====
    pdf.bloque_titulo("Datos del Cliente")

    cliente = estancia.cliente

    nombre_cliente = (
        f"{cliente.nombre} {cliente.apellidos or ''}"
    ).strip()

    campo(pdf, "Nombre", nombre_cliente, 95)

    campo(pdf, "DNI", cliente.dni, 95, salto=True)

    campo(pdf, "Teléfono", cliente.telefono, 95)
    campo(pdf, "Dirección", cliente.direccion, 95, salto=True)

    campo(pdf, "Población", cliente.poblacion, 95)
    campo(pdf, "Cod. Postal", cliente.codigo_postal, 95, salto=True)

    campo(pdf, "Provincia", cliente.provincia, 95, salto=True)

    pdf.ln(2)

    # ===== MASCOTA =====
    pdf.bloque_titulo("Datos de la Mascota")

    mascota = estancia.mascota

    campo2(pdf, "Nombre", mascota.nombre if mascota else "", 95)
    campo2(pdf, "Chip", getattr(mascota, "numero_chip", "") if mascota else "", 95, salto=True)

    campo2(pdf, "Raza", mascota.raza if mascota else "", 95)
    campo2(pdf, "Edad", mascota.edad if mascota else "", 95, salto=True)

    campo2(pdf, "Tamaño", mascota.tamano if mascota else "", 95)
    campo2(pdf, "Sexo", mascota.sexo if mascota else "", 95, salto=True)

    campo2(pdf, "Vacunas", mascota.vacunas if mascota else "", 95)
    campo2(pdf, "Medicación", getattr(mascota, "enfermedades_medicacion", "") if mascota else "", 95, salto=True)

    campo2(pdf, "Comp. Personas", getattr(mascota, "comportamiento_personas", "") if mascota else "", 95)
    campo2(pdf, "Comp. Perros", getattr(mascota, "comportamiento_perros", "") if mascota else "", 95, salto=True)

    pdf.ln(2)

    # ===== SERVICIOS =====
    pdf.bloque_titulo("Servicios y Totales")

    fecha_entrada = estancia.fecha_entrada.strftime("%d/%m/%Y") if estancia.fecha_entrada else ""
    fecha_salida = estancia.fecha_salida.strftime("%d/%m/%Y") if estancia.fecha_salida else ""

    dias = int(estancia.num_dias or 0)

    precio_dia = float(estancia.precio_dia or 0)
    subtotal = float(estancia.subtotal or 0)
    total = float(estancia.total or 0)

    tipo_tarifa = getattr(estancia, "tipo_precio_dia", None) or "normal"

    campo(pdf, "Fecha Entrada", fecha_entrada, 65)
    campo(pdf, "Fecha Salida", fecha_salida, 65)
    campo(pdf, "Hora Salida", getattr(estancia, "hora_salida", "") or "", 60, salto=True)

    campo(pdf, "Días Estancia", dias, 65)
    campo(pdf, "Precio Día", f"{precio_dia:.2f} EUR", 65)
    campo(pdf, "Subtotal", f"{subtotal:.2f} EUR", 60, salto=True)

    campo(pdf, "Tarifa", tipo_tarifa, 65)
    campo(pdf, "Cámaras", f"{float(estancia.importe_camaras or 0):.2f} EUR", 65)
    campo(pdf, "Veterinario", f"{float(estancia.importe_veterinario or 0):.2f} EUR", 60, salto=True)

    campo(pdf, "Pienso", f"{float(estancia.importe_pienso or 0):.2f} EUR", 65)
    campo(pdf, "Transporte", f"{float(estancia.importe_transporte or 0):.2f} EUR", 65)
    campo(pdf, "Extras", estancia.extras or "Sin extras", 60, salto=True)

    campo(pdf, "Importe Extras", f"{float(estancia.importe_extras or 0):.2f} EUR", 65, salto=True)

    pdf.ln(3)

    # ===== TOTAL =====
    total = float(estancia.total or 0)
    pagado = total if estancia.pagado else 0
    pendiente = total - pagado

    pdf.total_box(total, pagado, pendiente)

    # ===== PIE =====
    pdf.pie()

    pdf.output(output_path)
