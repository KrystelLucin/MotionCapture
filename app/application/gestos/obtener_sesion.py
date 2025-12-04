from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException

from app.application.gestos.gestor_sesiones import GestorSesiones
from app.domain.entities.gesto_sesion import GestoSesion

@dataclass(frozen=True)
class ObtenerSesionResponse:
    sesion_id: str
    tipo: str
    emocion: Optional[str]
    palabras_clave: List[str]
    duracion_segundos: float
    grabando: bool
    finalizado: bool
    creado_en: str
    cuenta_regresiva: Optional[int] = None
    frames_capturados: int = 0
    tiempo_restante: Optional[float] = None

class ObtenerSesion:
    def __init__(self, gestor: GestorSesiones):
        self.gestor = gestor

    def ejecutar(self, sesion_id: str) -> ObtenerSesionResponse:
        sesion: Optional[GestoSesion] = self.gestor.obtener(sesion_id)
        if not sesion:
            raise HTTPException(404, "Sesión no encontrada o ya expiró")

        tiempo_restante = None
        if sesion.grabando and sesion.inicio_grabacion and not sesion.finalizado:
            elapsed = (datetime.utcnow() - sesion.inicio_grabacion).total_seconds()
            tiempo_restante = round(max(0.0, sesion.duracion_segundos - elapsed), 1)

        return ObtenerSesionResponse(
            sesion_id=sesion.id,
            tipo=sesion.tipo.value,
            emocion=sesion.emocion,
            palabras_clave=sesion.palabras_clave,
            duracion_segundos=sesion.duracion_segundos,
            grabando=sesion.grabando,
            finalizado=sesion.finalizado,
            cuenta_regresiva=sesion.cuenta_regresiva,
            frames_capturados=len(sesion.frames),
            tiempo_restante=tiempo_restante,
            creado_en=sesion.creado_en.isoformat() + "Z",
        )