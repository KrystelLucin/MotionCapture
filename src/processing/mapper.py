from typing import Dict, Tuple
import math
import numpy as np

# Índices de landmarks (MediaPipe Pose)
NOSE = 0
L_ELBOW = 13
R_ELBOW = 14
L_SHOULDER = 11
R_SHOULDER = 12
L_WRIST = 15
R_WRIST = 16
L_HIP = 23
R_HIP = 24

# Ajustes de “sensibilidad” de cabeza
HEAD_GAIN_PITCH = 1.6
HEAD_GAIN_YAW   = 1.6
HEAD_GAIN_ROLL  = 1.3
HEAD_DEADZONE_DEG = 2.0  # elimina jitter pequeño

def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n


def _angle_in_plane(v: np.ndarray, axis1: np.ndarray, axis2: np.ndarray) -> float:
    """Proyecta v en plano (axis1, axis2) y devuelve ángulo atan2 en grados."""
    x = np.dot(v, axis1)
    y = np.dot(v, axis2)
    return math.degrees(math.atan2(y, x))

def _apply_deadzone(a_deg: float, dz_deg: float) -> float:
    if abs(a_deg) <= dz_deg:
        return 0.0
    return a_deg - dz_deg * math.copysign(1.0, a_deg)

def normalize_to_robot(value: float, min_angle: float, max_angle: float,
                       min_robot: int = 0, max_robot: int = 100) -> int:
    """Escala ángulos a [0–100] con clipping."""
    if max_angle == min_angle:
        return int((min_robot + max_robot) / 2)
    t = (value - min_angle) / (max_angle - min_angle)
    return int(np.clip(min_robot + t * (max_robot - min_robot), min_robot, max_robot))

def build_torso_axes(pose: Dict[int, Tuple[float, float, float]]):
    """Construye los ejes X, Y, Z del torso a partir de hombros y caderas."""
    Ls = np.array(pose[L_SHOULDER])
    Rs = np.array(pose[R_SHOULDER])
    Lh = np.array(pose[L_HIP])
    Rh = np.array(pose[R_HIP])

    center_shoulders = (Ls + Rs) / 2
    center_hips = (Lh + Rh) / 2

    X = _normalize(Rs - Ls)                        # eje X: hombros
    Y = _normalize(center_shoulders - center_hips) # eje Y: vertical torso
    Z = _normalize(np.cross(X, Y))                 # eje Z: normal al plano XY
    return X, Y, Z, center_shoulders


def head_angles(pose: Dict[int, Tuple[float, float, float]]) -> Tuple[int, int, int]:
    """Calcula (pitch, yaw, roll) de la cabeza usando vector nariz→centro hombros."""
    if pose is None or NOSE not in pose or L_SHOULDER not in pose or R_SHOULDER not in pose or L_HIP not in pose or R_HIP not in pose:
        return 50, 50, 50

    X, Y, Z, center_shoulders = build_torso_axes(pose)
    nose = np.array(pose[NOSE])
    V_head = _normalize(nose - center_shoulders)

    # Ángulos “geométricos”
    pitch_angle = _angle_in_plane(V_head, Y, Z)   # arriba/abajo (plano YZ)
    yaw_angle   = _angle_in_plane(V_head, X, Z)   # izquierda/derecha (plano XZ)
    roll_angle  = _angle_in_plane(V_head, X, Y)   # inclinación (plano XY)

    # Ganancia + deadzone + clamp
    pitch_angle = _apply_deadzone(pitch_angle * HEAD_GAIN_PITCH, HEAD_DEADZONE_DEG)
    yaw_angle   = _apply_deadzone(yaw_angle   * HEAD_GAIN_YAW,   HEAD_DEADZONE_DEG)
    roll_angle  = _apply_deadzone(roll_angle  * HEAD_GAIN_ROLL,  HEAD_DEADZONE_DEG)

    pitch = normalize_to_robot(np.clip(pitch_angle, -60, 60), -60, 60)
    yaw   = normalize_to_robot(np.clip(yaw_angle,   -60, 60), -60, 60)
    roll  = normalize_to_robot(np.clip(roll_angle,  -45, 45), -45, 45)
    return pitch, yaw, roll


def wing_channels(pose: Dict[int, Tuple[float, float, float]]) -> Tuple[int, int, int, int]:
    """Calcula (L.vertical, L.horizontal, R.vertical, R.horizontal) usando hombro→muñeca y torso."""
    if pose is None:
        return 50, 50, 50, 50

    X, Y, Z, _ = build_torso_axes(pose)
    
    Ls = np.array(pose[L_SHOULDER])
    Lw = np.array(pose[L_WRIST])
    Le = np.array(pose[L_ELBOW])
    Rs = np.array(pose[R_SHOULDER])
    Rw = np.array(pose[R_WRIST])
    Re = np.array(pose[R_ELBOW])

    V_left  = _normalize(0.7 * (Lw - Ls) + 0.3 * (Le - Ls))
    V_right = _normalize(0.7 * (Rw - Rs) + 0.3 * (Re - Rs))

    # Ala izquierda
    left_vertical   = _angle_in_plane(V_left, Y, Z)
    left_horizontal = float(np.clip(np.dot(V_left,  Z), -1.0, 1.0))
    Lv = 100 - normalize_to_robot(np.clip(left_vertical,  -90, 90), -90, 90)
    Lh = normalize_to_robot(-left_horizontal,  -0.8, 0.8)

    # Ala derecha
    right_vertical   = _angle_in_plane(V_right, Y, Z)
    right_horizontal = float(np.clip(np.dot(V_right, Z), -1.0, 1.0))
    Rv = 100 - normalize_to_robot(np.clip(right_vertical, -90, 90), -90, 90)
    Rh = normalize_to_robot(-right_horizontal, -0.8, 0.8)

    return Lv, Lh, Rv, Rh


def to_loly_pose(pose_lm: Dict, size: Tuple[int, int]) -> Dict:
    pitch, yaw, roll = head_angles(pose_lm)
    Lv, Lh, Rv, Rh = wing_channels(pose_lm)

    return {
        "head": {"pitch": pitch, "yaw": yaw, "row": roll},
        "wing_L": {"vertical": Lv, "horizontal": Lh},
        "wing_R": {"vertical": Rv, "horizontal": Rh}
    }
