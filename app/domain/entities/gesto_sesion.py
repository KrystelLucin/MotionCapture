from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import uuid
from app.domain.enums.gesture_type import GestureType

@dataclass
class FrameData:
    timestamp: float
    pose: Dict
    image_base64: str  # ← OBLIGATORIO para el video

@dataclass
class GestoSesion:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tipo: GestureType = GestureType.EMOTIONAL 
    emocion: Optional[str] = None
    palabras_clave: List[str] = field(default_factory=list)
    duracion_segundos: float = 5.0

    frames: List[FrameData] = field(default_factory=list)
    grabando: bool = False
    finalizado: bool = False
    cuenta_regresiva: Optional[int] = None
    inicio_grabacion: Optional[datetime] = None
    creado_en: datetime = field(default_factory=datetime.utcnow)