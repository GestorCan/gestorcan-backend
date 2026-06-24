from pathlib import Path
from reportlab.lib.units import cm
from reportlab.platypus import Spacer, Paragraph
from reportlab.platypus import Spacer, Paragraph, HRFlowable
from reportlab.lib import colors
#from app.pdf.clientes_pdf import PDFBase  # si lo tienes aquí
# o:
from app.utils.pdf_base import PDFBase

BASE_DIR = Path(__file__).resolve().parents[2]
LOGO_PATH = BASE_DIR / "static" / "logos" / "logo.png"


def generar_pdf_cliente(cliente, mascotas, output_path: str):
    residencia = {
        "nombre": "GestorCan Resort",
        "direccion": "Dirección de la residencia",
        "cif": "B00000000",
        "telefono": "600 000 000",
        "email": "info@gestorcan.com",
    }

    pdf = PDFBase(filename=output_path, titulo="Ficha de cliente")

    elementos = []

    elementos.append(pdf.cabecera(
        residencia=residencia,
        logo_path=str(LOGO_PATH)
    ))

    # resto igual...

    elementos.append(Spacer(1, 0.5 * cm))

    resumen = [
        ["Cliente", cliente.nombre],
        ["Mascotas", str(len(mascotas))],
        ["Última estancia", "—"],  # luego lo automatizamos
    ]

    tabla_resumen = pdf.tabla_datos(resumen)

    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 10))

    elementos.append(pdf.titulo_seccion("Datos del Cliente"))

    elementos.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor("#D1D5DB"),
        spaceBefore=2,
        spaceAfter=8
    ))

    datos_cliente = [
        ("Nombre", cliente.nombre),
        ("DNI / CIF", cliente.dni),
        ("Teléfono", cliente.telefono),
        ("Email", cliente.email),
        ("Dirección", cliente.direccion),
        ("Población", cliente.poblacion),
        ("Código Postal", cliente.codigo_postal),
        ("Observaciones", cliente.observaciones),
    ]

    elementos.append(pdf.tabla_datos(datos_cliente))

    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(pdf.titulo_seccion("Mascotas"))
    elementos.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor("#D1D5DB"),
        spaceBefore=2,
        spaceAfter=8
    ))

    headers = [
        "Nombre",
        "Raza",
        "Sexo",
        "Tamaño",
        "Nacimiento",
        "Observaciones",
    ]

    filas_mascotas = []

    if mascotas:
        for mascota in mascotas:
            filas_mascotas.append([
                mascota.nombre or "",
                mascota.raza or "",
                mascota.sexo or "",
                mascota.tamano or "",
                mascota.fecha_nacimiento or "",
                mascota.observaciones or "",
            ])
    else:
        filas_mascotas.append([
            "-", "-", "-", "-", "-", "Sin mascotas registradas"
        ])

    tabla_mascotas = pdf.tabla_factura(
        headers=headers,
        rows=filas_mascotas,
        col_widths=[
            3 * cm,
            3 * cm,
            2 * cm,
            2.2 * cm,
            2.8 * cm,
            4 * cm,
        ]
    )

    elementos.append(tabla_mascotas)

    pdf.construir(elementos)

    return output_path