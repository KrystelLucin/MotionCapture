import os
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from app.application.stories.ssml_generator import generate_ssml
from app.infrastructure.storage.azure_storage import AzureStorageService  # Usamos para subir

def configure_azure_tts():
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv('api_key'),
        region=os.getenv('region')
    )
    return speech_config

def text_to_audio(text_data, output_file, voice="es-MX-DaliaNeural"):
    speech_config = configure_azure_tts()

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    ssml = generate_ssml(text_data, voice)

    result = synthesizer.speak_ssml_async(ssml).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Audio saved: {output_file}")
    elif result.reason == speechsdk.ResultReason.Canceled:
        print(f"Error: {result.cancellation_details.error_details}")
    else:
        print(f"Error: {result.reason}")

def generate_audios(emotions_data, audio_dir):
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    for idx, text_data in enumerate(emotions_data):
        output_file = os.path.join(audio_dir, f"sentence_{idx}.wav")
        text_to_audio(text_data, output_file)

def combine_audios(audio_dir, output_audio):
    final_audio = None
    files = sorted([file for file in os.listdir(audio_dir) if file.startswith("sentence_") and file.endswith(".wav")],
                   key=lambda x: int(x.split("_")[1].split(".")[0]))

    if not files:
        print("No audio files found.")
        return

    for file in files:
        audio = AudioSegment.from_wav(os.path.join(audio_dir, file))
        final_audio = audio if final_audio is None else final_audio + audio

    if final_audio:
        final_path = os.path.join(audio_dir, output_audio)
        final_audio.export(final_path, format="wav")
        print(f"Combined audio saved: {output_audio}")

# Nueva función para subir a nube
def upload_to_cloud(storage_service: AzureStorageService, file_path, container, blob_name):
    with open(file_path, "rb") as f:
        url = storage_service._subir(container, f.read(), blob_name)
    return url