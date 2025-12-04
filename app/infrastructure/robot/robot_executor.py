import threading
from .audio_player import play_wav_blocking
from .serial_controller import SerialController

class RobotExecutor:
    def __init__(self, serial_port: str = "/dev/ttyUSB0"):
        self.serial = SerialController(serial_port)

    def execute(self, audio_path: str, movements_data: list):
        def run():
            # Iniciar audio y movimientos en paralelo
            audio_thread = threading.Thread(target=play_wav_blocking, args=(audio_path,))
            serial_thread = threading.Thread(target=self.serial.send_frames, args=(movements_data,))

            audio_thread.start()
            serial_thread.start()

            audio_thread.join()
            serial_thread.join()

        threading.Thread(target=run, daemon=True).start()