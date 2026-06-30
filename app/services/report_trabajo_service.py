from pathlib import Path
from datetime import datetime
from fpdf import FPDF
from sqlalchemy import text
from datetime import datetime, date


def formatear_fecha(valor):
    if not valor:
        return ""

    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")

    if isinstance(valor, str):
        for formato in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(valor, formato).strftime("%d/%m/%Y")
            except ValueError:
                pass

    return str(valor)




class InformeTrabajoPDF(FPDF):
    def __init__(self, fecha_informe: str):
        super().__init__(orientation="L", format="A4")
        self.fecha_informe = fecha_informe
        self.set_auto_page_break(auto=True, margin=10)
        self.add_page()

        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "Informe Entradas / Salidas", ln=True)

        self.set_font("Helvetica", "", 8)
        self.cell(0, 6, f"Fecha: {self.fecha_informe}", ln=True)

        self.ln(3)
        self._leyenda_colores()
        self.ln(8)
        self._render_table_header()



    def ajustar_texto(self, texto, ancho):
        texto = str(texto) if texto is not None else ""
        if self.get_string_width(texto) <= ancho - 1:
            return texto

        sufijo = "..."
        while texto and self.get_string_width(texto + sufijo) > ancho - 1:
            texto = texto[:-1]

        return texto + sufijo

    def _leyenda_colores(self):
        leyendas = [
            ("Lavado", (204, 229, 255)),
            ("Agresivo", (255, 204, 153)),
            ("Veterinario", (255, 204, 204)),
            ("Cámaras", (230, 204, 255)),
            ("Transporte", (204, 255, 204)),
        ]

        self.set_font("Helvetica", "", 7)

        for texto, color in leyendas:
            self.set_fill_color(*color)
            self.cell(35, 7, texto, border=1, fill=True)
            self.cell(3)

        self.ln(2)

    def _render_table_header(self):
        self.set_fill_color(200, 200, 200)
        self.set_font("Helvetica", "B", 6)

        headers = [
            ("Cliente", 30),
            ("Mascota", 20),
            ("Tamaño", 12),
            ("Entrada", 16),
            ("Salida/Hora", 22),
            ("Hab.", 9),
            ("Imp. Día", 12),
            ("Días", 8),
            ("Obs.", 18),
            ("Extras", 20),
            ("Imp. Extras", 12),
            ("Cámaras", 11),
            ("Vet.", 11),
            ("Transp.", 11),
            ("Total", 12),
            ("Pagado", 11),
            ("Carácter", 18),
            ("Población", 18),
        ]

        self.col_widths = [w for _, w in headers]

        for h, w in headers:
            self.cell(w, 6, h, border=1, fill=True, align="C")

        self.ln()

    def obtener_color_fila(self, fila):
        extras = (fila.extras or "").lower()
        comp_perros = (fila.comportamiento_perros or "").lower()
        comp_personas = (fila.comportamiento_personas or "").lower()

        camaras = float(fila.camaras or 0)
        veterinario = float(fila.veterinario or 0)
        transporte = float(fila.transporte or 0)

        if transporte > 0:
            return (204, 255, 204)
        elif "agresivo" in comp_perros or "agresivo" in comp_personas:
            return (255, 204, 153)
        elif camaras > 0:
            return (230, 204, 255)
        elif "lavado" in extras:
            return (204, 229, 255)
        elif veterinario > 0:
            return (255, 204, 204)

        return None






    def agregar_fila(self, fila):
        color_fila = self.obtener_color_fila(fila)

        self.set_font("Helvetica", "", 6)

        entrada_fmt = formatear_fecha(fila.entrada)
        salida_fmt = formatear_fecha(fila.salida)
        salida = f"{salida_fmt} {fila.hora_salida or ''}".strip()

        caracter = fila.comportamiento_perros or fila.comportamiento_personas or ""

        valores = [
            fila.cliente,
            fila.mascota,
            fila.tamano,
            entrada_fmt,
            salida,
            fila.habitacion,
            fila.precio_dia,
            fila.dias,
            fila.observaciones,
            fila.extras,
            fila.import_extras,
            fila.camaras,
            fila.veterinario,
            fila.transporte,
            fila.total,
            fila.pagado,
            caracter,
            fila.poblacion,
        ]

        for i, (v, w) in enumerate(zip(valores, self.col_widths)):
            texto = self.ajustar_texto(v, w)

            align = "C" if i in [2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15] else "L"

            if color_fila:
                self.set_fill_color(*color_fila)
                self.cell(w, 5, texto, border=1, fill=True, align=align)
            else:
                self.cell(w, 5, texto, border=1, fill=False, align=align)

        self.ln()


def generar_informe_trabajo_pdf(db, fecha=None) -> str:
    if fecha is None:
        fecha = datetime.now().date()

    fecha_str = fecha.strftime("%Y-%m-%d")
    fecha_archivo = fecha.strftime("%d-%m-%Y")

    query = text("""
        SELECT
            c.nombre AS cliente,
            c.apellidos AS apellidos,
            m.nombre AS mascota,
            m.tamano AS tamano,
            e.fecha_entrada AS entrada,
            e.fecha_salida AS salida,
            e.habitacion AS habitacion,
            e.precio_dia,
            e.num_dias AS dias,
            e.observaciones,
            e.extras,
            e.importe_extras AS import_extras,
            e.importe_camaras AS camaras,
            e.importe_veterinario AS veterinario,
            e.importe_transporte AS transporte,
            e.total,
            e.pagado,
            e.hora_salida,
            c.poblacion,
            m.comportamiento_perros,
            m.comportamiento_personas
        FROM estancias e
        JOIN clientes c ON e.cliente_id = c.id
        JOIN mascotas m ON e.mascota_id = m.id
        WHERE DATE(e.fecha_entrada) = :fecha
           OR DATE(e.fecha_salida) = :fecha
        ORDER BY e.fecha_entrada
    """)

    filas = db.execute(query, {"fecha": fecha_str}).fetchall()

    pdf = InformeTrabajoPDF(fecha_str)

    if filas:
        for fila in filas:
            pdf.agregar_fila(fila)
    else:
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 10, "No hay reservas.", ln=True)

    base_dir = Path(__file__).resolve().parents[1]
    carpeta = base_dir / "reports" / "autoreports"
    carpeta.mkdir(parents=True, exist_ok=True)

    archivo = carpeta / f"informe_trabajo_{fecha_archivo}.pdf"
    pdf.output(str(archivo))

    return str(archivo)