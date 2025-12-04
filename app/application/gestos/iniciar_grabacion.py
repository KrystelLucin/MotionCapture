from fastapi import HTTPException
from app.application.gestos.gestor_sesiones import GestorSesiones
from app.infrastructure.video.gesture_recorder import GestureRecorder
from app.domain.entities.gesto_sesion import GestoSesion

class IniciarStreamGrabacion:
    def __init__(self, gestor: GestorSesiones, recorder: GestureRecorder):
        self.gestor = gestor
        self.recorder = recorder

    def _obtener_y_validar(self, sesion_id: str) -> GestoSesion:
        sesion = self.gestor.obtener(sesion_id)
        if not sesion:
            raise HTTPException(404, "Sesión no encontrada")
        if sesion.finalizado:
            raise HTTPException(400, "La sesión ya fue finalizada")
        if sesion.grabando:
            raise HTTPException(400, "Ya hay una grabación en curso")
        return sesion

    def ejecutar(self, sesion_id: str):
        sesion = self._obtener_y_validar(sesion_id)
        return self.recorder.stream_with_countdown(sesion, self.gestor)