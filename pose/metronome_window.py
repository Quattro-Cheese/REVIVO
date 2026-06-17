from __future__ import annotations

import argparse
import threading
import time
import tkinter as tk

CLICK_INTERVAL_SEC = 0.5
CLICK_BPM = int(60 / CLICK_INTERVAL_SEC)


class MetronomeWindow:
    def __init__(self, root: tk.Tk, bpm: int) -> None:
        self.root = root
        self.bpm = CLICK_BPM
        self.interval_ms = int(CLICK_INTERVAL_SEC * 1000)
        self.interval_sec = CLICK_INTERVAL_SEC
        self.running = True
        self.stop_event = threading.Event()

        root.title("CPR Metronome")
        root.geometry("260x180")
        root.resizable(False, False)

        self.title = tk.Label(root, text="CPR Metronome", font=("Arial", 16, "bold"))
        self.title.pack(pady=(18, 4))

        self.bpm_label = tk.Label(
            root,
            text=f"{self.bpm} BPM / 0.5 sec",
            font=("Arial", 20, "bold"),
        )
        self.bpm_label.pack(pady=4)

        self.indicator = tk.Canvas(root, width=58, height=58, highlightthickness=0)
        self.indicator.pack(pady=8)
        self.circle = self.indicator.create_oval(6, 6, 52, 52, fill="#94A3B8", outline="")

        self.toggle_button = tk.Button(root, text="Pause", width=12, command=self.toggle)
        self.toggle_button.pack(pady=(2, 8))

        root.protocol("WM_DELETE_WINDOW", self.close)
        self.worker = threading.Thread(target=self.metronome_loop, daemon=True)
        self.worker.start()

    def toggle(self) -> None:
        self.running = not self.running
        self.toggle_button.config(text="Pause" if self.running else "Start")

    def close(self) -> None:
        self.stop_event.set()
        self.root.destroy()

    def metronome_loop(self) -> None:
        next_tick = time.perf_counter() + 0.2

        while not self.stop_event.is_set():
            if not self.running:
                next_tick = time.perf_counter() + self.interval_sec
                self.stop_event.wait(0.05)
                continue

            now = time.perf_counter()
            wait_sec = next_tick - now
            if wait_sec > 0:
                self.stop_event.wait(wait_sec)
                continue

            try:
                self.root.after(0, self.flash)
            except tk.TclError:
                break

            next_tick += self.interval_sec
            now = time.perf_counter()
            while next_tick <= now:
                next_tick += self.interval_sec

    def flash(self) -> None:
        self.indicator.itemconfig(self.circle, fill="#22C55E")
        self.root.after(100, self.reset_flash)

    def reset_flash(self) -> None:
        self.indicator.itemconfig(self.circle, fill="#94A3B8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bpm", type=int, default=120)
    args = parser.parse_args()

    root = tk.Tk()
    MetronomeWindow(root, max(1, args.bpm))
    root.mainloop()


if __name__ == "__main__":
    main()
