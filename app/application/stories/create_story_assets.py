import os
import json
import logging
from typing import Dict

from app.application.stories.emotion_analysis import analyze_emotions
from app.application.stories.gesture_selection import select_gestures
from app.infrastructure.external.audio.text_to_speech import (
    generate_audios,
    combine_audios,
    upload_to_cloud,
)
from app.infrastructure.external.audio.audio_utils import clean_wav_files, report_time
from app.infrastructure.storage.azure_storage import AzureStorageService
from app.infrastructure.storage.enums.container import Container

log = logging.getLogger(__name__)


def create_story_assets(
    story_text: str,
    gestures_base_path: str,
    temp_dir: str,
    storage_service: AzureStorageService,
) -> Dict[str, str]:
    """
    Orquesta todo el flujo para generar:
    - Audio completo del cuento
    - Movimientos (gestos) sincronizados
    - Texto del cuento
    Y los sube a Azure Blob Storage.

    Returns:
        Dict con URLs públicas de: audio, movements.txt y story_text.txt
    """
    os.makedirs(temp_dir, exist_ok=True)

    report_time("Starting emotion analysis")
    emotions_data = analyze_emotions(story_text)
    report_time("Emotion analysis completed")

    report_time("Generating individual audio sentences")
    generate_audios(emotions_data, temp_dir)
    report_time("Individual audios generated")

    report_time("Combining audio into final story.wav")
    combine_audios(temp_dir, "story.wav")
    report_time("Audio combined")

    report_time("Selecting and synchronizing gestures")
    gestures_with_segments = select_gestures(
        gestures_path=gestures_base_path,
        audio_dir=temp_dir,
        emotions_data=emotions_data,
    )
    report_time("Gestures selected and synchronized")

    # Guardar movimientos como TXT legible
    movements_path = os.path.join(temp_dir, "movements.txt")
    with open(movements_path, "w", encoding="utf-8") as f:
        json.dump(gestures_with_segments, f, indent=4, ensure_ascii=False)

    # Guardar texto original
    text_path = os.path.join(temp_dir, "story_text.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(story_text)

    # Subir todo a la nube
    audio_url = upload_to_cloud(
        storage_service=storage_service,
        file_path=os.path.join(temp_dir, "story.wav"),
        container=Container.CUENTOS.value,
        blob_name="story_audio.wav",
    )

    movements_url = upload_to_cloud(
        storage_service=storage_service,
        file_path=movements_path,
        container=Container.CUENTOS.value,
        blob_name="movements.txt",
    )

    text_url = upload_to_cloud(
        storage_service=storage_service,
        file_path=text_path,
        container=Container.CUENTOS.value,
        blob_name="story_text.txt",
    )

    # Limpieza opcional
    clean_wav_files(temp_dir)

    log.info("Story assets created and uploaded successfully")
    report_time("Story assets creation completed")

    return {
        "audio_url": audio_url,
        "movements_url": movements_url,
        "text_url": text_url,
    }