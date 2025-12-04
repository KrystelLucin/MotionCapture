# app/application/gestos/aprobar_gesto.py
from dataclasses import dataclass
import json
from fastapi import HTTPException
from app.application.gestos.gestor_sesiones import GestorSesiones
from app.infrastructure.storage.azure_storage import AzureStorageService

@dataclass(frozen=True)
class AprobarGestoRequest:
    sesion_id: str
    nombre: str

@dataclass
class AprobarGestoResponse:
    mensaje: str
    url: str
    frames: int

class AprobarGesto:
    def __init__(self, gestor: GestorSesiones, azure: AzureStorageService):
        self.gestor = gestor
        self.azure = azure

    def ejecutar(self, request: AprobarGestoRequest) -> AprobarGestoResponse:
        sesion = self.gestor.obtener(request.sesion_id)
        if not sesion or not sesion.finalizado:
            raise HTTPException(400, "Sesión no finalizada")

        movimientos = [
            {"time": f.timestamp, **f.pose} for f in sesion.frames
        ]
        if not movimientos:
            raise HTTPException(400, "No hay movimientos para guardar")

        json_data = json.dumps(movimientos, ensure_ascii=False, indent=2).encode()

        url = self.azure.subir_gesto(
            data=json_data,
            filename=f"{request.nombre}.json",
            tipo=sesion.tipo
        )

        self.gestor.eliminar(request.sesion_id)

        return AprobarGestoResponse(
            mensaje="Gesto guardado permanentemente",
            url=url,
            frames=len(movimientos)
        )