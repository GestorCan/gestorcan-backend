from app.database import SessionLocal
from app.models.configuracion_autoreport import ConfiguracionAutoreport

db = SessionLocal()

cfg = db.query(ConfiguracionAutoreport).first()

if not cfg:
    cfg = ConfiguracionAutoreport(
        activo=True,
        hora_envio="21:00",
        destinatarios="cualqueda2505@gmail.com,carlosojedaartieda@gmail.com",
        dias_adelante=1,
        dias_ocupacion=7
    )

    db.add(cfg)
    db.commit()

print("Configuración creada")