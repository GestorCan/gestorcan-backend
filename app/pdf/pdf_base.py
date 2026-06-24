from fpdf import FPDF
from datetime import datetime
import os

class PDFBase(FPDF):

    def cabecera(self, titulo, numero, fecha=None):
        # Logo (si existe)
        try:
            self.image("static/logos/logo.png", 10, 8, 30)
        except:
            pass
        from datetime import date, datetime

        if fecha is None:
            fecha = date.today()

        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

        fecha_texto = fecha.strftime("%d/%m/%Y")

        # Empresa (derecha)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, "Can Resort Málaga S.L.", 0, 1, "R")

        self.set_font("Arial", "", 8)
        self.cell(0, 5, "CIF: B21840988", 0, 1, "R")
        self.cell(0, 5, "Camino del Cortijuelo 26", 0, 1, "R")
        self.cell(0, 5, "29591 Campanillas (Málaga)", 0, 1, "R")
        self.cell(0, 5, "Tel: 672 71 39 50", 0, 1, "R")

        self.ln(5)

        # Título documento
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, titulo, 0, 1, "C")

        self.ln(3)

        # Nº y fecha
        from datetime import date, datetime

        if fecha is None:
            fecha = date.today()

        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

        fecha_texto = fecha.strftime("%d/%m/%Y")
        self.set_font("Arial", "", 10)
        self.cell(0, 6, f"Nº: {numero}", 0, 1)
        self.cell(0, 6, f"Fecha: {fecha.strftime('%d/%m/%Y')}", 0, 1)

        self.ln(3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def bloque_titulo(self, texto):
        self.set_font("Arial", "B", 11)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 6, texto, 0, 1, "L", True)
        self.ln(2)

    def fila(self, label, valor):
        self.set_font("Arial", "B", 9)
        self.cell(40, 5, f"{label}:", 0, 0)

        self.set_font("Arial", "", 9)
        self.cell(0, 5, str(valor), 0, 1)

    def total_box(self, total, pagado, pendiente):
        self.ln(5)
        self.set_font("Arial", "B", 12)

        self.cell(0, 8, f"TOTAL: {total:.2f} EUR", 0, 1, "R")

        self.set_font("Arial", "", 10)
        self.cell(0, 6, f"Pagado: {pagado:.2f} EUR", 0, 1)
        self.cell(0, 6, f"Pendiente: {pendiente:.2f} EUR", 0, 1)

    def pie(self):
        self.ln(10)
        self.set_font("Arial", "I", 8)
        self.cell(0, 5, "Gracias por confiar en Can Resort", 0, 1, "C")