from __future__ import annotations

from typing import Optional


def generate_voice_feedback(
    bpm: Optional[float],
    depth_cm: Optional[float],
    posture_correct: bool,
) -> str:
    if not posture_correct:
        return "팔을 곧게 펴세요."

    if depth_cm is None:
        return "압박 깊이를 측정 중입니다."

    if depth_cm < 5.0:
        return "더 깊게 압박하세요."

    if depth_cm > 6.0:
        return "힘을 조금 줄이세요."

    if bpm is None:
        return "압박 속도를 측정 중입니다."

    if bpm < 100:
        return "조금 더 빠르게 압박하세요."

    if bpm > 120:
        return "속도가 빠릅니다."

    return ""