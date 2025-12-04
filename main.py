# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# ------------------------------------------------------------------
# Configuración de logging (muy útil en producción y desarrollo)
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("loly-api")

# ------------------------------------------------------------------
# App
# ------------------------------------------------------------------
app = FastAPI(
    title="Loly – Cuentacuentos Robot",
    description="API para generar y reproducir cuentos personalizados con el robot físico",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------
# CORS – necesario para que tu app Expo (Android/iOS/web) pueda conectar
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambia por tu dominio o IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Database init (solo una vez al arrancar)
# ------------------------------------------------------------------
from app.infrastructure.database import init_db

@app.on_event("startup")
async def on_startup():
    logger.info("Iniciando API de Loly...")
    try:
        init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        raise

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------
from app.api.v1.endpoints.cuentos import router as cuentos_router
from app.api.v1.endpoints.gestos import router as gestos_router

app.include_router(cuentos_router, prefix="/api/v1", tags=["cuentos"])
app.include_router(gestos_router, prefix="/api/v1", tags=["gestos"])

# ------------------------------------------------------------------
# Ruta de salud (muy útil para monitoreo y Docker)
# ------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "loly-api"}

@app.get("/")
async def root():
    return {"message": "Loly API corriendo correctamente", "docs": "/docs"}