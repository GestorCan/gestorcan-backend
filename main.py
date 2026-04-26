from fastapi import FastAPI
from database import engine, Base
from models import Cliente

app = FastAPI()

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"mensaje": "GestorCan funcionando 🐶"}

@app.get("/clientes")
def obtener_clientes():
    return {"mensaje": "Listado de clientes"}
