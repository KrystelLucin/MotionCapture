# app/application/stories/play_story.py
from dataclasses import dataclass
from app.domain.entities.cuento import Cuento
from app.infrastructure.persistence.repositories.cuento_repo import CuentoRepository
from app.application.stories.download_assets import download_story_assets
from app.infrastructure.robot.robot_executor import RobotExecutor

@dataclass
class PlayStory:
    cuento_repo: CuentoRepository
    robot_executor: RobotExecutor

    def execute(self, cuento_id: int) -> None:
        cuento: Cuento = self.cuento_repo.obtener_por_id(cuento_id)
        if not cuento or not cuento.audio_url or not cuento.movimientos_url:
            raise ValueError("Cuento no encontrado o no está listo")

        # 1. Descargar archivos temporalmente
        audio_path, movements_data = download_story_assets(cuento)

        # 2. Ejecutar en el robot (bloqueante, pero en background)
        self.robot_executor.execute(audio_path, movements_data)