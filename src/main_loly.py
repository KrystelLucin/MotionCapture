import time
import serial
import serial.tools.list_ports as port_list

from capture.video_capture import VideoCapture
from processing.mapper import to_loly_pose

class EMA:
    def __init__(self, alpha=0.35, init=50):
        self.a = alpha
        self.y = init
    def __call__(self, x):
        self.y = self.a * x + (1 - self.a) * self.y
        return int(round(self.y))

f_pitch = EMA(); f_yaw = EMA(); f_roll = EMA()
f_Lv = EMA(); f_Lh = EMA(); f_Rv = EMA(); f_Rh = EMA()

def main():
    # Configuración de puerto serie
    port_robotis = "COM6"   # ajusta según corresponda
    baudrate = 1000000
    serialPort = serial.Serial(
        port=port_robotis, baudrate=baudrate,
        bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE
    )

    vc = VideoCapture(draw_debug=True)  # True para ver landmarks
    idop = 2  # ID de operación

    try:
        while True:
            lf = vc.read()
            if lf is None:
                print("⚠️ No se pudo leer de la cámara")
                break

            pose = to_loly_pose(lf.pose_landmarks, lf.image_size)

            posPitch = int(pose["head"]["pitch"])
            posYaw   = int(pose["head"]["yaw"])
            posRoll  = int(pose["head"]["row"])
            posAlaL_v = int(pose["wing_L"]["vertical"])
            posAlaL_h = int(pose["wing_L"]["horizontal"])
            posAlaR_v = int(pose["wing_R"]["vertical"])
            posAlaR_h = int(pose["wing_R"]["horizontal"])
            posPico   = 0 
            
            posPitch = f_pitch(posPitch)
            posYaw   = f_yaw(posYaw)
            posRoll  = f_roll(posRoll)
            posAlaL_v = f_Lv(posAlaL_v)
            posAlaL_h = f_Lh(posAlaL_h)
            posAlaR_v = f_Rv(posAlaR_v)
            posAlaR_h = f_Rh(posAlaR_h)
            
            trama = bytearray([
                idop, posPitch, posYaw, posRoll,
                posAlaL_v, posAlaL_h, posAlaR_v, posAlaR_h, posPico
            ])

            print("Enviando:", list(trama))
            serialPort.write(trama)

            time.sleep(0.05)  # ~20 Hz

    except KeyboardInterrupt:
        print("⏹️ Interrumpido por el usuario")
    finally:
        vc.release()
        serialPort.close()

if __name__ == "__main__":
    main()
