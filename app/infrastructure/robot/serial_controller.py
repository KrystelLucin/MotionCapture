# app/infrastructure/robot/serial_controller.py
import serial
import time
from typing import List, Dict

class SerialController:
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 1000000):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def open(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)

    def send_frames(self, frames: List[Dict]):
        self.open()
        try:
            for frame in frames:
                self.ser.write(frame["trama"])
                time.sleep(frame["duracion"])
        finally:
            self.ser.close()