# app/application/gestos/generar_preview.py
from app.infrastructure.video.video_encoder import crear_video_preview
from app.infrastructure.storage.azure_storage import AzureStorageService
from app.domain.entities.gesto_sesion import GestoSesion

class GenerarPreviewVideo:
    def __init__(self, azure: AzureStorageService):
        self.azure = azure

    def ejecutar(self, sesion: GestoSesion) -> str:
        if not sesion.frames:
            raise ValueError("No hay frames")

        video_path = crear_video_preview(sesion.frames)
        
        with open(video_path, "rb") as f:
            url = self.azure._subir(
                container="gestos",
                data=f.read(),
                blob_name=f"preview/{sesion.id}.mp4"
            )
        
        import os
        os.unlink(video_path)  # borrar temporal
        return url