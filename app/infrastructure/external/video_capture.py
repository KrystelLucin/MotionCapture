from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_face = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

@dataclass
class LandmarksFrame:
    raw: any                                      # frame original BGR
    annotated: any = None                         # ← NUEVO: frame con landmarks dibujados
    image_size: Tuple[int, int] = (0, 0)
    pose_landmarks: Optional[Dict[int, Tuple[float, float, float]]] = None
    face_landmarks: Optional[Dict[int, Tuple[float, float, float]]] = None

class VideoCapture:
    def __init__(self, cam_index: int = 1, draw_landmarks: bool = True):  # ← ahora por defecto True
        self.cap = cv2.VideoCapture(cam_index)
        self.draw_landmarks = draw_landmarks
        self.pose = mp_pose.Pose(
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def read(self) -> Optional[LandmarksFrame]:
        ok, frame_bgr = self.cap.read()
        if not ok:
            return None

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        pose_result = self.pose.process(rgb)

        # Convertir landmarks a dict
        pose_dict = None
        if pose_result.pose_landmarks:
            pose_dict = {i: (lm.x, lm.y, lm.z) for i, lm in enumerate(pose_result.pose_landmarks.landmark)}

        # Frame anotado (con landmarks)
        annotated = frame_bgr.copy()
        if self.draw_landmarks and pose_result.pose_landmarks:
            mp_drawing.draw_landmarks(
                annotated,
                pose_result.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )

        return LandmarksFrame(
            raw=frame_bgr.copy(),
            annotated=annotated,           # ← este es el que usamos en el stream
            image_size=frame_bgr.shape[:2][::-1],
            pose_landmarks=pose_dict,
            face_landmarks=None
        )