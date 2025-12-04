# app/application/stories/stream_story_to_robot.py
from app.infrastructure.robot.connection_manager import manager
from app.infrastructure.robot.trama_sender import stream_movements_to_robot
from app.infrastructure.persistence.repositories.cuento_repo import CuentoRepository

class StreamStoryToRobot:
    def __init__(self, cuento_repo: CuentoRepository):
        self.cuento_repo = cuento_repo

    async def execute(self, cuento_id: int):
        cuento = self.cuento_repo.get_by_id(cuento_id)
        if not cuento or not cuento.movimientos_url:
            return False

        await stream_movements_to_robot(cuento_id, cuento.movimientos_url)
        return True