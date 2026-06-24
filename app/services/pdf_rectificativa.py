from fpdf import FPDF
from pathlib import Path
import os
from app.models.residencias import Residencia


def limpiar_texto_pdf(valor):
    if valor is None:
        return ""

    return (
        str(valor)
        .replace("\u200b", "")
        .replace("\ufeff", "")
        .replace("€", "EUR")
    )







def generar_pdf_rectificativa(
    factura,
    factura_original,
    cliente,
    residencia
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # aquí ya usas residencia



    # LOGO
    logo_path = "static/logos/logo.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=22)

    # EMISOR
    pdf.set_xy(38, 10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 5, limpiar_texto_pdf(f"Nombre: {residencia.razon_social}"), ln=True)

    pdf.set_x(38)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, limpiar_texto_pdf(f"CIF: {residencia.cif}"), ln=True)
    pdf.set_x(38)
    pdf.cell(0, 5, limpiar_texto_pdf(f"Direccion: {residencia.direccion}"), ln=True)
    pdf.set_x(38)
    pdf.cell(0, 5, limpiar_texto_pdf(f"Telefono: {residencia.telefono}"), ln=True)
    pdf.cell(0, 5, limpiar_texto_pdf(f"Email: {residencia.email}"), ln=True)

    # TITULO
    pdf.set_xy(125, 10)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(70, 8, "FACTURA RECTIFICATIVA", ln=True, align="R")

    pdf.set_x(125)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(70, 6, f"N: {factura.numero_factura}", ln=True, align="R")
    pdf.set_x(125)
    pdf.cell(70, 6, f"Fecha: {factura.fecha}", ln=True, align="R")

    pdf.ln(20)

    # CLIENTE
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "DATOS DEL CLIENTE", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(
        0,
        6,
        limpiar_texto_pdf(f"Cliente: {cliente.nombre} {cliente.apellidos or ''}"),
        ln=True
    )

    pdf.cell(0, 6, f"DNI/CIF: {getattr(cliente, 'dni', '') or '-'}", ln=True)
    pdf.cell(0, 6, f"Telefono: {getattr(cliente, 'telefono', '') or '-'}", ln=True)
    pdf.cell(0, 6, f"Email: {getattr(cliente, 'email', '') or '-'}", ln=True)

    pdf.ln(6)

    # FACTURA ORIGINAL
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "FACTURA RECTIFICADA", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Factura original: {factura_original.numero_factura}", ln=True)
    pdf.cell(0, 6, f"Fecha original: {factura_original.fecha}", ln=True)
    pdf.cell(0, 6, f"Tipo rectificativa: {factura.tipo_rectificativa or 'I'}", ln=True)

    pdf.multi_cell(
        0,
        6,
        limpiar_texto_pdf(f"Motivo: {factura.motivo_rectificacion or '-'}")
    )

    pdf.ln(6)

    # TABLA IMPORTES
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(80, 8, "Concepto", border=1)
    pdf.cell(35, 8, "Base", border=1, align="R")
    pdf.cell(35, 8, "IVA", border=1, align="R")
    pdf.cell(35, 8, "Total", border=1, align="R", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(80, 8, "Rectificacion factura", border=1)
    pdf.cell(35, 8, f"{float(factura.base_imponible):.2f} EUR", border=1, align="R")
    pdf.cell(35, 8, f"{float(factura.iva):.2f} EUR", border=1, align="R")
    pdf.cell(35, 8, f"{float(factura.total):.2f} EUR", border=1, align="R", ln=True)

    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(
        0,
        8,
        f"TOTAL RECTIFICATIVA: {float(factura.total):.2f} EUR",
        ln=True,
        align="R"
    )

    # QR si existe
    if factura.qr_path and os.path.exists(factura.qr_path):
        pdf.image(factura.qr_path, x=160, y=230, w=35)

    pdf.set_y(250)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0,
        5,
        "Factura rectificativa emitida conforme al sistema VeriFactu. "
        "Documento generado electronicamente."
    )

    carpeta = Path("media/facturas_rectificativas")
    carpeta.mkdir(parents=True, exist_ok=True)

    ruta = carpeta / f"{factura.numero_factura}.pdf"
    pdf.output(str(ruta))

    return str(ruta)