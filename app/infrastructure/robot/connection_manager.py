from fastapi import Request
from typing import Dict
import asyncio

class RobotConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Request] = {}  # cuento_id -> Request

    async def connect(self, cuento_id: int, request: Request):
        await request.accept()
        self.active_connections[cuento_id] = request
        print(f"Robot conectado para cuento {cuento_id}")

    def disconnect(self, cuento_id: int):
        self.active_connections.pop(cuento_id, None)
        print(f"Robot desconectado del cuento {cuento_id}")

    async def send_trama(self, cuento_id: int, trama: bytes, duration: float):
        request = self.active_connections.get(cuento_id)
        if request and not request.is_disconnected():
            await request.send_text(f"data: {trama.hex()},{duration}\n\n")
            await asyncio.sleep(duration)  # ¡Sincronización perfecta!

    async def send_audio_start(self, cuento_id: int, audio_url: str):
        request = self.active_connections.get(cuento_id)
        if request and not request.is_disconnected():
            await request.send_text(f"event: audio\n")
            await request.send_text(f"data: {audio_url}\n\n")

manager = RobotConnectionManager()