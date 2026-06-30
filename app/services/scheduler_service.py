import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.autoreport_service import ejecutar_autoreport


scheduler = BackgroundScheduler(timezone="Europe/Madrid")


def iniciar_scheduler():
    if scheduler.running:
        return

    hora_env = os.getenv("AUTOREPORT_HORA", "21:00")
    hora, minuto = hora_env.split(":")

    scheduler.add_job(
        ejecutar_autoreport,
        CronTrigger(
            hour=int(hora),
            minute=int(minuto),
            timezone="Europe/Madrid"
        ),
        id="autoreport_diario",
        replace_existing=True
    )

    scheduler.start()

    print(f"Scheduler iniciado. Autoreport diario a las {hora_env}.")


def parar_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler detenido.")