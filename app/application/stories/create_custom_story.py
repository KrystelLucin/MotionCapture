import uuid
from app.application.stories.create_story_assets import create_story_assets
from app.domain.entities.cuento import Cuento
from app.infrastructure.persistence.repositories.cuento_repo import CuentoRepository
from app.infrastructure.storage.azure_storage import AzureStorageService

class CreateCustomStory:
    def __init__(
        self,
        story_repo: CuentoRepository,
        storage_service: AzureStorageService,
    ):
        self.story_repo = story_repo
        self.storage_service = storage_service

    def execute(self, request) -> Cuento:
        # 1. Generar los assets (audio + movimientos + texto)
        assets = create_story_assets(
            story_text=request.text,
            gestures_base_path="gestures",
            temp_dir=f"tmp/story_{uuid.uuid4().hex[:12]}",
            storage_service=self.storage_service,
        )

        # 2. Guardar el cuento en base de datos
        story = Cuento(
            title=request.title,
            text=request.text,
            audio_url=assets["audio_url"],
            movements_url=assets["movements_url"],
            text_url=assets["text_url"],
            created_by=request.created_by or "anonymous",
            is_custom=True,
        )

        return self.story_repo.guardar(story)