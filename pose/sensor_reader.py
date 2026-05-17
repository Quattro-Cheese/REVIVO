import serial
import time


class UltrasonicReader:
    def __init__(self, port="COM13", baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        time.sleep(2)
        self.distance_cm = None

    def update(self):
        while self.ser.in_waiting > 0:
            line = self.ser.readline().decode(errors="ignore").strip()

            if not line.startswith("DIST:"):
                continue

            try:
                value = line.replace("DIST:", "")
                self.distance_cm = float(value)
            except ValueError:
                continue

        return self.distance_cm

    def close(self):
        self.ser.close()