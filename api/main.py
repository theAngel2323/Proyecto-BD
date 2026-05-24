from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.logging_config import setup_logging
from config.database import test_connection

from api.routers import auth, pacientes, citas, prescripciones, ingresos, inventario

# Inicializar logging
setup_logging()


app = FastAPI(
    title="HospitalDB API",
    description="Sistema Integrado de Gestión Hospitalaria — BD2 UPANA",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # En producción: poner la URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router,           prefix="/api/auth",           tags=["Autenticación"])
app.include_router(pacientes.router,      prefix="/api/pacientes",      tags=["Pacientes"])
app.include_router(citas.router,          prefix="/api/citas",          tags=["Citas"])
app.include_router(prescripciones.router, prefix="/api/prescripciones", tags=["Prescripciones"])
app.include_router(ingresos.router,       prefix="/api/ingresos",       tags=["Ingresos"])
app.include_router(inventario.router,     prefix="/api/inventario",     tags=["Inventario"])



@app.get("/", tags=["Estado"])
def root():
    db_ok = test_connection()
    return {
        "sistema": "HospitalDB API",
        "estado":  "online",
        "base_de_datos": "conectada" if db_ok else "error",
    }