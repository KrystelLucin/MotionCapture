# app/application/gestos/preview_gesto.py
from dataclasses import dataclass
from fastapi import HTTPException
import os
from app.application.gestos.gestor_sesiones import GestorSesiones
from app.infrastructure.storage.azure_storage import AzureStorageService
from app.infrastructure.video.video_encoder import crear_video_preview

@dataclass
class PreviewGestoRequest:
    sesion_id: str

@dataclass
class PreviewGestoResponse:
    video_url: str
    frames: int

class PreviewGesto:
    def __init__(self, gestor: GestorSesiones, azure: AzureStorageService):
        self.gestor = gestor
        self.azure = azure

    def ejecutar(self, request: PreviewGestoRequest) -> PreviewGestoResponse:
        sesion = self.gestor.obtener(request.sesion_id)
        if not sesion or not sesion.finalizado:
            raise HTTPException(400, "La grabación no ha finalizado")

        if not sesion.frames:
            raise HTTPException(400, "No hay frames grabados")

        # Generar video
        video_path = crear_video_preview(sesion.frames)

        # Subir como temporal (expira en 1 hora)
        with open(video_path, "rb") as f:
            video_url = self.azure.subir_temporal(
                data=f.read(),
                filename=f"preview_{sesion.id}.mp4",
                expires_in_hours=1
            )

        os.unlink(video_path)
        return PreviewGestoResponse(video_url=video_url, frames=len(sesion.frames))