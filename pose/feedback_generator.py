from __future__ import annotations

from typing import Optional


def generate_voice_feedback(
    bpm: Optional[float],
    depth_cm: Optional[float],
    posture_correct: bool,
) -> str:
    """
    여러 문제가 동시에 발생했을 때 모든 문제를 반영하되,
    TTS 시간이 길어지지 않도록 짧은 문장으로 압축한다.

    - 문제 1개: 해당 피드백 출력
    - 문제 2개: 두 피드백을 짧게 결합
    - 문제 3개: 종합 피드백 출력
    """

    posture_issue = False
    depth_issue = ""
    speed_issue = ""

    # 자세 문제
    if not posture_correct:
        posture_issue = True

    # 깊이 문제
    if depth_cm is not None:
        if depth_cm < 5.0:
            depth_issue = "shallow"
        elif depth_cm > 6.0:
            depth_issue = "deep"

    # 속도 문제
    if bpm is not None:
        if bpm < 100:
            speed_issue = "slow"
        elif bpm > 120:
            speed_issue = "fast"

    issues = []

    if posture_issue:
        issues.append("posture")

    if depth_issue:
        issues.append("depth")

    if speed_issue:
        issues.append("speed")

    # 문제가 없으면 출력 없음
    if not issues:
        return ""

    # 문제가 3개 이상이면 짧은 종합 피드백
    if len(issues) >= 3:
        return "팔, 깊이, 속도를 함께 조정하세요."

    # 문제가 2개인 경우
    if len(issues) == 2:
        if posture_issue and depth_issue == "shallow":
            return "팔을 펴고, 더 깊게 압박하세요."

        if posture_issue and depth_issue == "deep":
            return "팔을 펴고, 힘을 조금 줄이세요."

        if posture_issue and speed_issue == "fast":
            return "팔을 펴고, 속도를 줄이세요."

        if posture_issue and speed_issue == "slow":
            return "팔을 펴고, 조금 더 빠르게 압박하세요."

        if depth_issue == "shallow" and speed_issue == "fast":
            return "더 깊게, 조금 천천히 압박하세요."

        if depth_issue == "shallow" and speed_issue == "slow":
            return "더 깊고 빠르게 압박하세요."

        if depth_issue == "deep" and speed_issue == "fast":
            return "힘을 줄이고, 속도를 낮추세요."

        if depth_issue == "deep" and speed_issue == "slow":
            return "힘은 줄이고, 조금 더 빠르게 압박하세요."

    # 문제가 1개인 경우
    if posture_issue:
        return "팔을 곧게 펴세요."

    if depth_issue == "shallow":
        return "더 깊게 압박하세요."

    if depth_issue == "deep":
        return "힘을 조금 줄이세요."

    if speed_issue == "slow":
        return "조금 더 빠르게 압박하세요."

    if speed_issue == "fast":
        return "속도가 빠릅니다."

    return ""