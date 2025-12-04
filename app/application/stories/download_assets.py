import requests
from pathlib import Path
import json
import tempfile

def download_story_assets(cuento) -> tuple[str, list]:
    temp_dir = Path(tempfile.gettempdir()) / "loly_cuentos"
    temp_dir.mkdir(exist_ok=True)

    # Descargar audio
    audio_path = temp_dir / f"cuento_{cuento.id}_audio.wav"
    audio_path.write_bytes(requests.get(cuento.audio_url).content)

    # Descargar movimientos
    movements_raw = requests.get(cuento.movimientos_url).text

    # Detectar formato automáticamente
    try:
        movements_data = json.loads(movements_raw)
    except json.JSONDecodeError:
        # Si es .txt plano, lo parseamos
        movements_data = parse_txt_movements(movements_raw)

    return str(audio_path), movements_data


def parse_txt_movements(text: str) -> list[dict]:
    # Ejemplo de formato: "02a03c50... 0.04"
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            hex_str, duration = parts[0], float(parts[1])
            result.append({
                "trama": bytes.fromhex(hex_str),
                "duracion": duration
            })
    return result