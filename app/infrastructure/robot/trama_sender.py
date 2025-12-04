import requests
from .connection_manager import manager

async def stream_movements_to_robot(cuento_id: int, movements_url: str):
    """Descarga el movements.txt y lo envía trama por trama"""
    try:
        response = requests.get(movements_url)
        response.raise_for_status()
        data = response.json()  # asumiendo que movements.txt es JSON válido

        await manager.send_audio_start(cuento_id, data[0]["audio_url"])  # opcional

        for segmento in data:
            for gesto in segmento["gestos"]:
                for frame_name, frame_data in gesto["frames"].items():
                    # Construir trama como antes (9 bytes)
                    trama = bytearray([
                        2,  # ID fijo
                        frame_data["head"]["pitch"],
                        frame_data["head"]["yaw"],
                        frame_data["head"]["roll"],
                        frame_data["wing_L"]["vertical"],
                        frame_data["wing_L"]["horizontal"],
                        frame_data["wing_R"]["vertical"],
                        frame_data["wing_R"]["horizontal"],
                        50  # pico desactivado
                    ])
                    duracion = frame_data.get("duration", 0.04)  # 40ms por defecto
                    await manager.send_trama(cuento_id, bytes(trama), duracion)
    except Exception as e:
        print(f"Error enviando movimientos: {e}")