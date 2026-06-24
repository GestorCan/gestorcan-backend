## app/models/residencias.py

from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy import Float
class Residencia(Base):
    __tablename__ = "residencias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cif = Column(String)
    direccion = Column(String)
    telefono = Column(String)
    email = Column(String)
    web = Column(String)
    logo_url = Column(String)
    color_principal = Column(String, default="#3CB371")
    color_secundario = Column(String, default="#1E293B")
    iva_defecto = Column(Float, default=21.0)
    provincia = Column(String)
    codigo_postal = Column(String)
    pais = Column(String)

    razon_social = Column(String)

    iban = Column(String)
    swift = Column(String)

    serie_facturacion = Column(String, default="A")

    hora_checkin = Column(String, default="12:00")
    hora_checkout = Column(String, default="10:00")

    permite_compartidas = Column(Integer, default=1)
    permite_camaras = Column(Integer, default=1)

    max_mascotas = Column(Integer, default=0)
    activa = Column(Integer, default=1)