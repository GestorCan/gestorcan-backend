# app/verifactu/qr_service.py

import os
from pathlib import Path
import qrcode


from app.verifactu.config import QR_DIR



QR_DIR = Path("media/qr")
QR_DIR.mkdir(parents=True, exist_ok=True)


def generar_qr_factura(factura):

    QR_DIR.mkdir(parents=True, exist_ok=True)

    contenido_qr = (
        f"FACTURA:{factura.numero_factura}\n"
        f"FECHA:{factura.fecha}\n"
        f"TOTAL:{factura.total}\n"
        f"HASH:{factura.hash_actual}"
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=6,
        border=2
    )

    qr.add_data(contenido_qr)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    output_path = QR_DIR / f"factura_{factura.numero_factura}.png"

    img.save(str(output_path))

    return str(output_path)