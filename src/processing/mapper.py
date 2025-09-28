import math
import numpy as np
from typing import Dict, Tuple

# Índices de MediaPipe Pose
NOSE = 0
L_SHOULDER, R_SHOULDER = 11, 12
L_WRIST, R_WRIST       = 15, 16
MOUTH_L, MOUTH_R       = 9, 10

# ------------------ Tablas de calibración ------------------
CAL_TABLES = {
    "pitch": [(29.0,0), (37.0,50), (47.0,100)],          # plano ZY
    "yaw":   [(72.0,0), (90.0,50), (108.0,100)],         # plano XZ
    "roll":  [(83.0,0), (90.0,50), (97.0,100)],          # plano XY (ojo: si cambias método recalibra)
    "AL_v":  [(114.0,0), (90.0,50), (70.0,100)],         # XY
    "AL_h":  [(70.0,0), (90.0,50), (114.0,100)],         # ZX
    "AR_v":  [(-114.0,0), (-90.0,50), (-70.0,100)],      # XY
    "AR_h":  [(-70.0,0), (-90.0,50), (-114.0,100)],      # ZX
}

# ------------------ Utilidades ------------------
def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 1e-6 else v

def project_and_angle(v: np.ndarray, i: int, j: int) -> float:
    """
    Proyecta el vector v en el plano definido por e_i, e_j y devuelve atan2(comp_j, comp_i) en grados.
    Ej: (Y,Z) => i=1, j=2
    """
    p = np.array([0.0, 0.0, 0.0])
    p[i] = v[i]; p[j] = v[j]
    n = np.linalg.norm(p)
    if n < 1e-6:
        return 0.0
    p /= n
    return math.degrees(math.atan2(p[j], p[i]))

def interp_lookup(angle: float, table: list[tuple[float,int]]) -> int:
    """Interpola en tabla (ángulo, valor) con N puntos calibrados."""
    if not table:
        return 50
    table = sorted(table, key=lambda p: p[0])
    if angle <= table[0][0]:
        return table[0][1]
    if angle >= table[-1][0]:
        return table[-1][1]
    for (a1,v1),(a2,v2) in zip(table, table[1:]):
        if a2 == a1:  # evita división por cero
            continue
        if (a1 <= angle <= a2) or (a1 >= angle >= a2):  # soporta crec/decrec
            t = (angle - a1) / (a2 - a1)
            return int(round(v1 + t*(v2 - v1)))
    return table[-1][1]

def apply_deadzone_servo(value: int, center: int = 50, dz: int = 2) -> int:
    """Deadzone en espacio servo (0..100)."""
    return center if abs(value - center) < dz else value

def has_keys(pose, keys):
    return pose is not None and all(k in pose for k in keys)

# ------------------ Ángulos crudos ------------------
def raw_pitch(pose):
    if not has_keys(pose, [NOSE,L_SHOULDER,R_SHOULDER]): return 37.0
    nose = np.array(pose[NOSE]); Ls = np.array(pose[L_SHOULDER]); Rs = np.array(pose[R_SHOULDER])
    center = (Ls + Rs) / 2.0
    v = _normalize(nose - center)
    return project_and_angle(v, 1, 2)  # (Y,Z)

def raw_yaw(pose):
    if not has_keys(pose, [NOSE,L_SHOULDER,R_SHOULDER]): return 90.0
    nose = np.array(pose[NOSE]); Ls = np.array(pose[L_SHOULDER]); Rs = np.array(pose[R_SHOULDER])
    center = (Ls + Rs) / 2.0
    v = _normalize(nose - center)
    return project_and_angle(v, 0, 2)  # (X,Z)

def raw_roll(pose):
    if not has_keys(pose, [MOUTH_L,MOUTH_R]): return 90.0
    ml = np.array(pose[MOUTH_L]); mr = np.array(pose[MOUTH_R])
    u = mr - ml; u[2] = 0.0
    if np.linalg.norm(u[:2]) < 1e-6:
        return 90.0
    return project_and_angle(u, 0, 1)  # (X,Y)

def raw_AL_v(pose):
    if not has_keys(pose, [L_SHOULDER,L_WRIST]): return 90.0
    Ls = np.array(pose[L_SHOULDER]); Lw = np.array(pose[L_WRIST])
    v = _normalize(Ls - Lw)  # invertido
    return project_and_angle(v, 0, 1)  # (X,Y)

def raw_AL_h(pose):
    if not has_keys(pose, [L_SHOULDER,L_WRIST]): return 90.0
    Ls = np.array(pose[L_SHOULDER]); Lw = np.array(pose[L_WRIST])
    v = _normalize(Ls - Lw)  # invertido
    return project_and_angle(v, 0, 2)  # (X,Z)

def raw_AR_v(pose):
    if not has_keys(pose, [R_SHOULDER,R_WRIST]): return -90.0
    Rs = np.array(pose[R_SHOULDER]); Rw = np.array(pose[R_WRIST])
    v = _normalize(Rw - Rs)
    return project_and_angle(v, 0, 1)  # (X,Y)

def raw_AR_h(pose):
    if not has_keys(pose, [R_SHOULDER,R_WRIST]): return -90.0
    Rs = np.array(pose[R_SHOULDER]); Rw = np.array(pose[R_WRIST])
    v = _normalize(Rw - Rs)
    return project_and_angle(v, 0, 2)  # (X,Z)

# ------------------ Salida final ------------------
def to_loly_pose(pose_lm: Dict[int, Tuple[float,float,float]], size: Tuple[int,int]) -> Dict:
    pitch = interp_lookup(raw_pitch(pose_lm), CAL_TABLES["pitch"])
    yaw   = interp_lookup(raw_yaw(pose_lm),   CAL_TABLES["yaw"])
    roll  = interp_lookup(raw_roll(pose_lm),  CAL_TABLES["roll"])
    Lv    = interp_lookup(raw_AL_v(pose_lm),  CAL_TABLES["AL_v"])
    Lh    = interp_lookup(raw_AL_h(pose_lm),  CAL_TABLES["AL_h"])
    Rv    = interp_lookup(raw_AR_v(pose_lm),  CAL_TABLES["AR_v"])
    Rh    = interp_lookup(raw_AR_h(pose_lm),  CAL_TABLES["AR_h"])

    # aplica deadzone antes de devolver
    pitch = apply_deadzone_servo(pitch)
    yaw   = apply_deadzone_servo(yaw)
    roll  = apply_deadzone_servo(roll)
    Lv    = apply_deadzone_servo(Lv)
    Lh    = apply_deadzone_servo(Lh)
    Rv    = apply_deadzone_servo(Rv)
    Rh    = apply_deadzone_servo(Rh)

    return {
        "head": {"pitch": pitch, "yaw": yaw, "row": roll},
        "wing_L": {"vertical": Lv, "horizontal": Lh},
        "wing_R": {"vertical": Rv, "horizontal": Rh}
    }
