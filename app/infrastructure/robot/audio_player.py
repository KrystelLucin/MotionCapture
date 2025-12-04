from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio as play

def play_wav_blocking(path: str):
    audio = AudioSegment.from_wav(path)
    play(audio) 