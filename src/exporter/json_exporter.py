from typing import Dict, List
import json


def build_gesture_json(gesture_id: str, labels: List[str], frames: List[Dict]) -> Dict:
    data = {
        "gesture_id": gesture_id,
        "labels": labels,
        "duration": frames[-1]["timestamp"] if frames else 0.0,
        "frames": {}
    }
    for i, fr in enumerate(frames):
        data["frames"][f"Position{i}"] = fr
    return data


def save_gesture_json(payload: Dict, out_path: str) -> None:
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)