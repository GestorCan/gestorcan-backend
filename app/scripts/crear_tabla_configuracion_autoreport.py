from app.database import engine, Base
from app.models.configuracion_autoreport import ConfiguracionAutoreport

print("BASE DE DATOS USADA:", engine.url)

Base.metadata.create_all(bind=engine)

print("Tabla configuracion_autoreport creada/verificada correctamente.")