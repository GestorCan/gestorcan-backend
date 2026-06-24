from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT


class PDFBase:
    def __init__(self, filename: str, titulo: str = "Documento"):
        self.filename = filename
        self.titulo = titulo

        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name="TituloPDF",
            fontSize=18,
            leading=22,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=12,
        ))

        self.styles.add(ParagraphStyle(
            name="Seccion",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#111827"),
            spaceBefore=14,
            spaceAfter=6,
        ))

        self.styles.add(ParagraphStyle(
            name="Texto",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#111827"),
        ))

    def cabecera(self, residencia: dict, logo_path: str | None = None):
        izquierda = []

        if logo_path:
            try:
                logo = Image(logo_path, width=3.2 * cm, height=2.2 * cm)
                izquierda.append(logo)
            except Exception:
                pass

        izquierda.append(Paragraph(
            f"<font size='12'><b>{residencia.get('nombre', '')}</b></font>",
            self.styles["Texto"]
        ))
        izquierda.append(Paragraph(residencia.get("direccion", ""), self.styles["Texto"]))
        izquierda.append(Paragraph(f"CIF: {residencia.get('cif', '')}", self.styles["Texto"]))
        izquierda.append(Paragraph(f"Tel: {residencia.get('telefono', '')}", self.styles["Texto"]))
        izquierda.append(Paragraph(residencia.get("email", ""), self.styles["Texto"]))

        derecha = [
            Paragraph(f"<b>{self.titulo.upper()}</b>", self.styles["TituloPDF"])
        ]
        from datetime import datetime

        derecha = [
            Paragraph(f"<b>{self.titulo.upper()}</b>", self.styles["TituloPDF"]),
            Paragraph(datetime.now().strftime("%d/%m/%Y"), self.styles["Texto"])
        ]

        tabla = Table(
            [[izquierda, derecha]],
            colWidths=[10 * cm, 7 * cm]
        )

        tabla.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            # Sin fondo negro
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),

            # Línea inferior elegante
            ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),

            ("ALIGN", (1, 0), (1, 0), "RIGHT"),

            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))

        return tabla

    def titulo_seccion(self, texto: str):
        return Paragraph(
            f"<font size='13'><b>{texto}</b></font>",
            self.styles["Seccion"]
        )

    def tabla_datos(self, datos: list[tuple[str, str]]):
        filas = []

        for etiqueta, valor in datos:
            filas.append([
                Paragraph(f"<b>{etiqueta}</b>", self.styles["Texto"]),
                Paragraph(str(valor or ""), self.styles["Texto"]),
            ])

        tabla = Table(
            filas,
            colWidths=[4 * cm, 13 * cm],
            hAlign="LEFT",
        )

        tabla.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),

            # ❌ quitamos fondo negro
            # ("BACKGROUND", (0, 0), (0, -1), ...)

            # ✔ etiquetas suaves
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#374151")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),

            # ✔ valores normales
            ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#111827")),

            # ✔ fondo ligero alterno (muy elegante)
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [
                colors.white,
                colors.HexColor("#F9FAFB"),
            ]),

            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.HexColor("#E5E7EB")),
        ]))

        return tabla

    def tabla_factura(self, headers: list[str], rows: list[list[str]], col_widths=None):
        data = [headers] + rows

        tabla = Table(
            data,
            colWidths=col_widths,
            hAlign="LEFT",
            repeatRows=1,
        )

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#E5E7EB")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#F9FAFB"),
            ]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        return tabla

    def construir(self, elementos: list):
        self.doc.build(elementos)