# app/infrastructure/video/gesture_recorder.py
import time
import base64
import cv2
from app.infrastructure.external.video_capture import VideoCapture
from app.infrastructure.video.mapper import to_loly_pose
from app.domain.entities.gesto_sesion import GestoSesion, FrameData
from datetime import datetime

class GestureRecorder:
    def __init__(self, cam_index=1):
        self.capture = VideoCapture(cam_index=cam_index, draw_debug=False)

    def stream_with_countdown(self, sesion: GestoSesion, gestor):
        # Cuenta regresiva
        for i in range(3, 0, -1):
            sesion.cuenta_regresiva = i
            gestor.guardar(sesion)
            yield {"type": "countdown", "data": i}
            time.sleep(1)

        # Inicio grabación
        sesion.cuenta_regresiva = None
        sesion.grabando = True
        sesion.inicio_grabacion = datetime.utcnow()
        sesion.frames = []
        gestor.guardar(sesion)

        start = time.time()
        while time.time() - start < sesion.duracion_segundos:
            frame = self.capture.read()
            if not frame or not frame.pose_landmarks:
                continue

            timestamp = time.time() - start
            pose_robot = to_loly_pose(frame.pose_landmarks, frame.image_size)

            # Usar la imagen YA ANOTADA por VideoCapture
            _, buffer = cv2.imencode('.jpg', cv2.resize(frame.annotated, (640, 480)))
            b64 = base64.b64encode(buffer).decode()

            sesion.frames.append(FrameData(timestamp, pose_robot, b64))
            gestor.guardar(sesion)

            yield {
                "type": "frame",
                "data": {
                    "image": b64,
                    "time_left": round(sesion.duracion_segundos - (time.time() - start), 1)
                }
            }

        sesion.grabando = False
        sesion.finalizado = True
        gestor.guardar(sesion)
        yield {"type": "finished", "data": len(sesion.frames)}