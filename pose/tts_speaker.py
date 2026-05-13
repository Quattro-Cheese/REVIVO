from __future__ import annotations

from typing import Optional


def generate_cpr_feedback(
    bpm: Optional[float],
    depth_cm: Optional[float],
    posture_correct: bool,
) -> str:
    messages = []

    if not posture_correct:
        messages.append("팔 자세를 곧게 유지하세요.")
    else:
        messages.append("팔 자세가 적절합니다.")

    if depth_cm is None:
        messages.append("압박 깊이를 측정 중입니다.")
    elif depth_cm < 5.0:
        messages.append("압박 깊이가 부족합니다. 조금 더 깊게 압박하세요.")
    elif depth_cm > 6.0:
        messages.append("압박 깊이가 과합니다. 힘을 조금 줄이세요.")
    else:
        messages.append("압박 깊이가 적절합니다.")

    if bpm is None:
        messages.append("압박 속도를 측정 중입니다.")
    elif bpm < 100:
        messages.append("압박 속도가 느립니다. 조금 더 빠르게 압박하세요.")
    elif bpm > 120:
        messages.append("압박 속도가 빠릅니다. 조금만 천천히 압박하세요.")
    else:
        messages.append("압박 속도가 적절합니다.")

    return " ".join(messages)