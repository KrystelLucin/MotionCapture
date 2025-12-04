# app/infrastructure/video/video_encoder.py
import cv2
import base64
import tempfile
import numpy as np
from typing import List
from app.domain.entities.gesto_sesion import FrameData

def crear_video_preview(frames: List[FrameData], fps: int = 30) -> str:
    if not frames:
        raise ValueError("No hay frames para generar video")

    # Decodificar primer frame para obtener tamaño
    first_img = base64.b64decode(frames[0].image_base64)
    nparr = np.frombuffer(first_img, np.uint8)
    sample = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = sample.shape[:2]

    # Crear archivo temporal
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    output_path = tmp_file.name
    tmp_file.close()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    for frame_data in frames:
        img_data = base64.b64decode(frame_data.image_base64)
        frame = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Opcional: dibujar timestamp
        cv2.putText(frame, f"{frame_data.timestamp:.2f}s", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        out.write(frame)

    out.release()
    return output_path