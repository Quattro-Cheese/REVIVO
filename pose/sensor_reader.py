import serial
import time
from math import isfinite


class UltrasonicReader:
    def __init__(
        self,
        port="COM13",
        baudrate=9600,
        min_distance_cm=2.0,
        max_distance_cm=40.0,
    ):
        self.min_distance_cm = min_distance_cm
        self.max_distance_cm = max_distance_cm

        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
            time.sleep(2)
            self.distance_cm = None
            self._dummy = False
        except Exception as e:
            print(f"⚠️  시리얼 포트 연결 실패 ({port}): {e}")
            print("⚠️  더미 모드로 실행합니다 (distance_cm = 12.0 고정)")
            self.ser = None
            self.distance_cm = 12.0
            self._dummy = True

    def update(self):
        if self._dummy:
            return self.distance_cm

        while self.ser.in_waiting > 0:
            line = self.ser.readline().decode(errors="ignore").strip()
            if not line.startswith("DIST:"):
                continue
            try:
                distance_cm = float(line.replace("DIST:", ""))
            except ValueError:
                continue
            if not isfinite(distance_cm):
                continue
            if not self.min_distance_cm <= distance_cm <= self.max_distance_cm:
                continue

            self.distance_cm = distance_cm
        return self.distance_cm

    def close(self):
        if self.ser:
            self.ser.close()
