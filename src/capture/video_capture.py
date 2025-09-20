from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_face = mp.solutions.face_mesh

@dataclass
class LandmarksFrame:
    image_size: Tuple[int, int]
    pose_landmarks: Optional[Dict[int, Tuple[float, float, float]]]
    face_landmarks: Optional[Dict[int, Tuple[float, float, float]]]

class VideoCapture:
    def __init__(self, cam_index: int = 1, draw_debug: bool = False):
        self.cap = cv2.VideoCapture(cam_index)
        self.draw_debug = draw_debug
        self.pose = mp_pose.Pose(model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.face = mp_face.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.drawing = mp.solutions.drawing_utils
        self.drawing_styles = mp.solutions.drawing_styles

    def read(self) -> Optional[LandmarksFrame]:
        ok, frame = self.cap.read()
        if not ok:
            return None
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pose_res = self.pose.process(rgb)
        face_res = self.face.process(rgb)

        pose_dict = None
        face_dict = None

        if pose_res.pose_landmarks:
            pose_dict = {}
            for i, lm in enumerate(pose_res.pose_landmarks.landmark):
                pose_dict[i] = (lm.x, lm.y, lm.z)

        if face_res.multi_face_landmarks and len(face_res.multi_face_landmarks) > 0:
            face_dict = {}
            for i, lm in enumerate(face_res.multi_face_landmarks[0].landmark):
                face_dict[i] = (lm.x, lm.y, lm.z)

        if self.draw_debug:
            vis = frame.copy()
            if pose_res.pose_landmarks:
                self.drawing.draw_landmarks(
                    vis,
                    pose_res.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.drawing_styles.get_default_pose_landmarks_style())
            if face_res.multi_face_landmarks:
                for fl in face_res.multi_face_landmarks:
                    self.drawing.draw_landmarks(
                        vis,
                        fl,
                        mp_face.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.drawing_styles.get_default_face_mesh_tesselation_style(),
                    )
            cv2.imshow('Loly Motion Capture [debug]', vis)
            cv2.waitKey(1)

        return LandmarksFrame(image_size=(w, h), pose_landmarks=pose_dict, face_landmarks=face_dict)

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()