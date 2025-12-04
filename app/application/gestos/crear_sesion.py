from dataclasses import dataclass
from typing import List
from app.domain.entities.gesto_sesion import GestoSesion
from app.domain.enums.gesture_type import GestureType
from app.application.gestos.gestor_sesiones import GestorSesiones

@dataclass(frozen=True)
class CrearSesionGestoRequest:
    tipo: GestureType
    emocion: str | None = None
    palabras_clave: List[str] | None = None
    duracion_segundos: float = 5.0

@dataclass
class CrearSesionGestoResponse:
    sesion_id: str
    tipo: str
    emocion: str | None
    palabras_clave: List[str]
    duracion_segundos: float
    creado_en: str

class CrearSesionGesto:
    def __init__(self, gestor: GestorSesiones):
        self.gestor = gestor

    def ejecutar(self, request: CrearSesionGestoRequest) -> CrearSesionGestoResponse:
        sesion = GestoSesion(
            tipo=request.tipo,
            emocion=request.emocion,
            palabras_clave=request.palabras_clave or [],
            duracion_segundos=request.duracion_segundos,
        )
        self.gestor.crear(sesion)

        return CrearSesionGestoResponse(
            sesion_id=sesion.id,
            tipo=sesion.tipo.value,
            emocion=sesion.emocion,
            palabras_clave=sesion.palabras_clave,
            duracion_segundos=sesion.duracion_segundos,
            creado_en=sesion.creado_en.isoformat(),
        )