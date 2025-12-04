from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Cuento:
    id: Optional[int] = None
    titulo: str = ""
    descripcion: Optional[str] = None
    texto: str = ""
    imagen_url: Optional[str] = None
    audio_url: Optional[str] = None
    movimientos_json_url: Optional[str] = None
    es_personalizado: bool = False
    creado_en: Optional[datetime] = None
    creado_por: Optional[str] = None

    def esta_listo_para_reproducir(self) -> bool:
        return bool(self.audio_url and self.movimientos_json_url)