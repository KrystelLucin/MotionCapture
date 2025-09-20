import time
import argparse
from typing import List

from capture.video_capture import VideoCapture
from processing.mapper import to_loly_pose
from exporter.json_exporter import build_gesture_json, save_gesture_json


def record_once(gesture_id: str, labels: List[str], seconds: float, debug: bool, out_file: str):
    vc = VideoCapture(draw_debug=debug)
    t0 = time.time()
    frames = []

    try:
        while True:
            lf = vc.read()
            if lf is None:
                print("⚠️ No se pudo leer de la cámara.")
                break
            now = time.time() - t0
            pose = to_loly_pose(lf.pose_landmarks, lf.face_landmarks, lf.image_size)

            frames.append({
                "timestamp": round(now, 3),
                "head": pose["head"],
                "wing_L": pose["wing_L"],
                "wing_R": pose["wing_R"],
            })

            if now >= seconds:
                break
    finally:
        vc.release()

    payload = build_gesture_json(gesture_id=gesture_id, labels=labels, frames=frames)
    save_gesture_json(payload, out_file)
    print(f"✅ Guardado: {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Loly Motion Capture — Fase 1")
    parser.add_argument("--gesture_id", type=str, default="Gesture001")
    parser.add_argument("--labels", nargs='*', default=["neutral"])  # ej: --labels joy surprise
    parser.add_argument("--seconds", type=float, default=3.0)
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("--out", type=str, default="data/samples/sample.json")
    args = parser.parse_args()

    record_once(
        gesture_id=args.gesture_id,
        labels=args.labels,
        seconds=args.seconds,
        debug=args.debug,
        out_file=args.out
    )