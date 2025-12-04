import json
from datetime import timedelta, datetime
import redis
from config.settings import settings
from app.domain.entities.gesto_sesion import GestoSesion, FrameData
from app.domain.enums.gesture_type import GestureType

class GestorSesiones:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def _key(self, sid): return f"gesto_sesion:{sid}"

    def crear(self, sesion: GestoSesion):
        data = {
            "id": sesion.id,
            "tipo": sesion.tipo.value,
            "emocion": sesion.emocion,
            "palabras_clave": sesion.palabras_clave,
            "duracion_segundos": sesion.duracion_segundos,
            "grabando": sesion.grabando,
            "finalizado": sesion.finalizado,
            "cuenta_regresiva": sesion.cuenta_regresiva,
            "inicio_grabacion": sesion.inicio_grabacion.isoformat() if sesion.inicio_grabacion else None,
            "creado_en": sesion.creado_en.isoformat(),
            "frames": [
                {
                    "timestamp": f.timestamp,
                    "pose": f.pose,
                    "image_base64": f.image_base64
                } for f in sesion.frames
            ]
        }
        self.redis.setex(self._key(sesion.id), timedelta(minutes=30), json.dumps(data))

    def obtener(self, sesion_id: str) -> GestoSesion | None:
        raw = self.redis.get(self._key(sesion_id))
        if not raw: return None
        data = json.loads(raw)

        frames = [
            FrameData(
                timestamp=f["timestamp"],
                pose=f["pose"],
                image_base64=f["image_base64"]
            ) for f in data.get("frames", [])
        ]

        return GestoSesion(
            id=data["id"],
            tipo=GestureType(data["tipo"]),
            emocion=data["emocion"],
            palabras_clave=data["palabras_clave"],
            duracion_segundos=data["duracion_segundos"],
            frames=frames,
            grabando=data["grabando"],
            finalizado=data["finalizado"],
            cuenta_regresiva=data["cuenta_regresiva"],
            inicio_grabacion=datetime.fromisoformat(data["inicio_grabacion"]) if data["inicio_grabacion"] else None,
            creado_en=datetime.fromisoformat(data["creado_en"].replace("Z", "+00:00")),
        )

    def guardar(self, sesion: GestoSesion): self.crear(sesion)
    def eliminar(self, sid: str): self.redis.delete(self._key(sid))