from __future__ import annotations

from typing import Optional


def generate_voice_feedback(
    bpm: Optional[float],
    depth_cm: Optional[float],
    posture_correct: bool,
) -> str:
    """
    여러 문제가 동시에 발생했을 때,
    문제를 모두 수집한 뒤 우선순위가 높은 피드백을 최대 2개까지 반환한다.

    우선순위:
    1. 자세 문제
    2. 깊이 문제
    3. 속도 문제
    """

    issues: list[tuple[int, str]] = []

    # 1순위: 자세 문제
    if not posture_correct:
        issues.append((1, "팔을 곧게 펴세요."))

    # 2순위: 압박 깊이 문제
    if depth_cm is not None:
        if depth_cm < 5.0:
            issues.append((2, "더 깊게 압박하세요."))
        elif depth_cm > 6.0:
            issues.append((2, "힘을 조금 줄이세요."))

    # 3순위: 압박 속도 문제
    if bpm is not None:
        if bpm < 100:
            issues.append((3, "조금 더 빠르게 압박하세요."))
        elif bpm > 120:
            issues.append((3, "속도가 빠릅니다."))

    # 문제가 없으면 음성 출력 없음
    if not issues:
        return ""

    # 우선순위 기준 정렬
    issues.sort(key=lambda x: x[0])

    # 한 번에 너무 많은 말을 하지 않도록 최대 2개까지만 안내
    selected_issues = issues[:2]

    # 문장만 추출해서 하나의 TTS 문장으로 합치기
    feedback_messages = [message for _, message in selected_issues]

    return " ".join(feedback_messages)