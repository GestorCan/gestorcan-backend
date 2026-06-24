from pathlib import Path
from datetime import datetime

from fpdf import FPDF

from app.models.factura import Factura
from app.verifactu.auditoria_service import verificar_cadena_hash


AUDITORIA_DIR = Path("app/verifactu/storage/auditoria")
AUDITORIA_DIR.mkdir(parents=True, exist_ok=True)


class AuditoriaPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Informe Auditoria VeriFactu", ln=True)

        self.set_font("Arial", "", 9)
        self.cell(
            0,
            6,
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            ln=True
        )

        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")


def cortar_hash(valor, longitud=18):
    if not valor:
        return "-"

    return f"{valor[:longitud]}..."


def generar_pdf_auditoria_verifactu(db):
    auditoria = verificar_cadena_hash(db)

    facturas = (
        db.query(Factura)
        .order_by(Factura.fecha.asc(), Factura.id.asc())
        .all()
    )

    pdf = AuditoriaPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Resumen
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Resumen", ln=True)

    pdf.set_font("Arial", "", 10)

    estado = (
        "Cadena Hash Correcta"
        if auditoria["cadena_valida"]
        else "Cadena Hash con errores"
    )

    pdf.cell(0, 7, f"Estado: {estado}", ln=True)
    pdf.cell(0, 7, f"Facturas verificadas: {auditoria['facturas_verificadas']}", ln=True)
    pdf.cell(0, 7, f"Errores detectados: {auditoria['errores_detectados']}", ln=True)
    pdf.set_font("Arial", "", 7)

    pdf.multi_cell(
        0,
        5,
        f"Primer hash: {auditoria.get('primer_hash') or '-'}"
    )

    pdf.multi_cell(
        0,
        5,
        f"Ultimo hash: {auditoria.get('ultimo_hash') or '-'}"
    )

    pdf.ln(6)

    # Tabla
    pdf.set_font("Arial", "B", 8)

    pdf.cell(32, 7, "Factura", border=1)
    pdf.cell(105, 7, "Hash anterior", border=1)
    pdf.cell(105, 7, "Hash actual", border=1)
    pdf.cell(30, 7, "Estado", border=1, ln=True)

    pdf.set_font("Arial", "", 6)

    for factura in facturas:
        pdf.cell(32, 7, factura.numero_factura or "-", border=1)

        pdf.cell(
            105,
            7,
            factura.hash_anterior or "-",
            border=1
        )

        pdf.cell(
            105,
            7,
            factura.hash_actual or "-",
            border=1
        )

        pdf.cell(
            30,
            7,
            "Valido" if auditoria["cadena_valida"] else "Revisar",
            border=1,
            ln=True
        )

    # Errores
    if auditoria["errores"]:
        pdf.ln(6)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Errores detectados", ln=True)

        pdf.set_font("Arial", "", 8)

        for error in auditoria["errores"]:
            pdf.multi_cell(
                0,
                6,
                (
                    f"Factura: {error['numero_factura']} | "
                    f"Campo: {error['campo']} | "
                    f"Esperado: {error['esperado']} | "
                    f"Encontrado: {error['encontrado']}"
                )
            )

    nombre = f"informe_auditoria_verifactu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    ruta = AUDITORIA_DIR / nombre

    pdf.output(str(ruta))

    return str(ruta)