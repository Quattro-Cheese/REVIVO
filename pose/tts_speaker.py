from __future__ import annotations

import subprocess
import time
import platform


class TTSSpeaker:
    def __init__(self, interval_sec: float = 2.5) -> None:
        self.interval_sec = interval_sec
        self.last_spoken_time = 0.0
        self.process: subprocess.Popen | None = None
        self._is_mac = platform.system() == "Darwin"
        self._is_windows = platform.system() == "Windows"

    def speak(self, message: str) -> None:
        if not message:
            return

        now = time.time()
        if now - self.last_spoken_time < self.interval_sec:
            return
        if self.process is not None and self.process.poll() is None:
            return

        self.last_spoken_time = now
        print("TTS SPEAK:", repr(message))

        try:
            if self._is_windows:
                safe_message = message.replace("'", "''")
                command = (
                    "Add-Type -AssemblyName System.Speech; "
                    "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    "$speaker.Rate = 0; "
                    "$speaker.Volume = 100; "
                    f"$speaker.Speak('{safe_message}');"
                )
                self.process = subprocess.Popen(
                    ["powershell", "-NoProfile", "-Command", command],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif self._is_mac:
                self.process = subprocess.Popen(
                    ["say", message],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # Linux 등 — 출력만
                pass
        except Exception as e:
            print(f"TTS 오류: {e}")
