from __future__ import annotations

import subprocess
import time


class TTSSpeaker:
    def __init__(self, interval_sec: float = 2.5) -> None:
        self.interval_sec = interval_sec
        self.last_spoken_time = 0.0
        self.process: subprocess.Popen[bytes] | None = None

    def speak(self, message: str) -> None:
        if not message:
            return

        now = time.time()

        # 너무 자주 말하지 않도록 제한
        if now - self.last_spoken_time < self.interval_sec:
            return

        # 이전 음성이 아직 재생 중이면 새 음성은 무시
        if self.process is not None and self.process.poll() is None:
            return

        self.last_spoken_time = now

        # PowerShell 문자열에서 작은따옴표 처리
        safe_message = message.replace("'", "''")

        command = (
            "Add-Type -AssemblyName System.Speech; "
            "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$speaker.Rate = 0; "
            "$speaker.Volume = 100; "
            f"$speaker.Speak('{safe_message}');"
        )

        print("TTS SPEAK:", repr(message))

        self.process = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )