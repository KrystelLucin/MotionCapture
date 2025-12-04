# src/infrastructure/storage/azure_storage.py
from azure.storage.blob import BlobServiceClient
from config.settings import settings
from app.infrastructure.storage.enums.container import Container
from app.domain.enums.gesture_type import GestureType
import uuid

from typing import Optional, List, Dict

class AzureStorageService:
    def __init__(self, connection_string: str = settings.AZURE_STORAGE_CONNECTION_STRING):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def _get_container_client(self, container: Container):
        client = self.blob_service_client.get_container_client(container.value)
        try:
            client.create_container()
        except Exception:
            pass
        return client

    # === SUBIR CUENTO (sin prefijo) ===
    def subir_cuento_archivo(self, data: bytes, filename: str) -> str:
        return self._subir(Container.CUENTOS, data, filename)

    # === SUBIR GESTO (con prefijo por tipo) ===
    def subir_gesto(
        self,
        data: bytes,
        filename: str,
        tipo: GestureType
    ) -> str:
        prefijo = f"{tipo.value}/"
        return self._subir(Container.GESTOS, data, f"{prefijo}{filename}")

    # === MÉTODO PRIVADO GENÉRICO ===
    def _subir(self, container: Container, data: bytes, blob_name: str) -> str:
        client = self._get_container_client(container)
        blob_client = client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True)
        return blob_client.url

    # === LISTAR GESTOS POR TIPO ===
    def listar_gestos_por_tipo(self, tipo: GestureType) -> List[Dict]:
        container_client = self._get_container_client(Container.GESTOS)
        prefijo = f"{tipo.value}/"
        
        blobs = container_client.list_blobs(name_starts_with=prefijo)
        return [
            {
                "nombre": blob.name.split("/")[-1],
                "url": container_client.get_blob_client(blob.name).url,
                "tipo": tipo.value
            }
            for blob in blobs
        ]

    # === BUSCAR GESTO POR NOMBRE ===
    def buscar_gesto(self, nombre: str, tipo: GestureType) -> Optional[str]:
        gestos = self.listar_gestos_por_tipo(tipo)
        for g in gestos:
            if g["nombre"] == nombre:
                return g["url"]
        return None