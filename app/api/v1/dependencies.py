# app/api/v1/dependencies.py
from functools import lru_cache
from app.application.gestos.gestor_sesiones import GestorSesiones
from app.infrastructure.storage.azure_storage import AzureStorageService
from app.infrastructure.video.gesture_recorder import GestureRecorder

@lru_cache()
def get_gestor_sesiones() -> GestorSesiones:
    return GestorSesiones()

@lru_cache()
def get_azure_storage() -> AzureStorageService:
    return AzureStorageService()

@lru_cache()
def get_gesture_recorder() -> GestureRecorder:
    return GestureRecorder(cam_index=1)  # o el que uses