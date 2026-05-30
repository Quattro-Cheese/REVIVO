from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

# MediaPipe Pose Landmark 인덱스
_LEFT_SHOULDER = 11
_RIGHT_SHOULDER = 12
_LEFT_ELBOW = 13
_RIGHT_ELBOW = 14
_LEFT_WRIST = 15
_RIGHT_WRIST = 16
_LEFT_HIP = 23
_RIGHT_HIP = 24

CORRECT_THRESHOLD = 163.0
INCORRECT_THRESHOLD = 157.0
VISIBILITY_THRESHOLD = 0.5

# 어깨 수직 판정: 어깨-손목 수평 오프셋이 어깨 너비의 이 비율 이하면 수직으로 판정
SHOULDER_VERTICAL_RATIO = 0.3


@dataclass
class PoseEvalResult:
    left_elbow_angle: float  # 왼팔 팔꿈치 각도 (-1이면 미감지)
    right_elbow_angle: float  # 오른팔 팔꿈치 각도 (-1이면 미감지)
    is_correct: bool  # 팔꿈치 각도 기준 정확 여부
    feedback: str  # 팔꿈치 피드백 메시지

    # [추가] 어깨 수직 여부
    shoulder_vertical: Optional[bool] = None
    shoulder_feedback: str = ""

    # [추가] 압박 구간 팔꿈치 유지 비율 (0.0~1.0, None이면 미측정)
    elbow_hold_ratio: Optional[float] = None
    elbow_hold_feedback: str = ""


class HysteresisJudge:
    def __init__(self) -> None:
        self._is_correct = False

    def update(self, angle: float) -> bool:
        if not self._is_correct and angle >= CORRECT_THRESHOLD:
            self._is_correct = True
        elif self._is_correct and angle < INCORRECT_THRESHOLD:
            self._is_correct = False
        return self._is_correct

    def reset(self) -> None:
        self._is_correct = False


class ElbowHoldTracker:
    """
    압박 구간(in_compression=True) 동안
    팔꿈치가 올바른 상태를 유지한 비율을 계산.

    RepCounter의 _in_compression 상태와 연동해서 사용.
    """

    def __init__(self) -> None:
        self._total_frames = 0
        self._correct_frames = 0
        self._in_compression = False
        self._last_ratio: Optional[float] = None

    def update(self, in_compression: bool, is_correct: bool) -> Optional[float]:
        """
        압박 구간이 끝날 때 비율을 반환.
        구간 중이면 None 반환.
        """
        if in_compression and not self._in_compression:
            # 압박 시작 → 카운터 초기화
            self._total_frames = 0
            self._correct_frames = 0
            self._in_compression = True

        if self._in_compression:
            self._total_frames += 1
            if is_correct:
                self._correct_frames += 1

        if not in_compression and self._in_compression:
            # 압박 종료 → 비율 계산
            self._in_compression = False
            if self._total_frames > 0:
                self._last_ratio = self._correct_frames / self._total_frames
                return self._last_ratio

        return None

    @property
    def last_ratio(self) -> Optional[float]:
        return self._last_ratio


def _to_pixel(lm, width: int, height: int) -> np.ndarray:
    return np.array([lm.x * width, lm.y * height])


def _calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    ba = a - b
    bc = c - b
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return float(np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0))))


def _check_shoulder_vertical(
    lm,
    frame_width: int,
    frame_height: int,
    vis: list[float],
) -> Optional[bool]:
    """
    어깨가 손목 위에 수직으로 위치하는지 판정.

    판정 기준:
    - 어깨 중점의 x좌표와 손목 중점의 x좌표 차이가
      어깨 너비의 SHOULDER_VERTICAL_RATIO 이하이면 수직으로 판정.
    - 측면 촬영 시 한쪽만 보여도 판정 가능하도록 설계.
    """
    left_vis = all(
        vis[i] >= VISIBILITY_THRESHOLD for i in [_LEFT_SHOULDER, _LEFT_WRIST]
    )
    right_vis = all(
        vis[i] >= VISIBILITY_THRESHOLD for i in [_RIGHT_SHOULDER, _RIGHT_WRIST]
    )

    if not left_vis and not right_vis:
        return None

    shoulder_pts = []
    wrist_pts = []

    if left_vis:
        shoulder_pts.append(_to_pixel(lm[_LEFT_SHOULDER], frame_width, frame_height))
        wrist_pts.append(_to_pixel(lm[_LEFT_WRIST], frame_width, frame_height))
    if right_vis:
        shoulder_pts.append(_to_pixel(lm[_RIGHT_SHOULDER], frame_width, frame_height))
        wrist_pts.append(_to_pixel(lm[_RIGHT_WRIST], frame_width, frame_height))

    shoulder_mid_x = float(np.mean([p[0] for p in shoulder_pts]))
    wrist_mid_x = float(np.mean([p[0] for p in wrist_pts]))

    # 어깨 너비 (양쪽 보일 때) 또는 고정값 사용
    if (
        vis[_LEFT_SHOULDER] >= VISIBILITY_THRESHOLD
        and vis[_RIGHT_SHOULDER] >= VISIBILITY_THRESHOLD
    ):
        left_sh = _to_pixel(lm[_LEFT_SHOULDER], frame_width, frame_height)
        right_sh = _to_pixel(lm[_RIGHT_SHOULDER], frame_width, frame_height)
        shoulder_width = float(np.linalg.norm(left_sh - right_sh))
    else:
        shoulder_width = frame_width * 0.2  # 어깨 너비 추정값

    if shoulder_width < 1e-3:
        return None

    offset_ratio = abs(shoulder_mid_x - wrist_mid_x) / shoulder_width
    return offset_ratio <= SHOULDER_VERTICAL_RATIO


def evaluate_pose(
    image_landmarks,
    frame_width: int,
    frame_height: int,
    visibilities: list[list[float]] | None = None,
    hysteresis: HysteresisJudge | None = None,
    elbow_tracker: ElbowHoldTracker | None = None,
    in_compression: bool = False,
) -> PoseEvalResult | None:
    if not image_landmarks:
        if hysteresis is not None:
            hysteresis.reset()
        return None

    lm = image_landmarks[0]
    vis = visibilities[0] if visibilities else [1.0] * 33

    # ── 팔꿈치 각도 판정 ──────────────────────────────
    left_visible = all(
        vis[i] >= VISIBILITY_THRESHOLD
        for i in [_LEFT_SHOULDER, _LEFT_ELBOW, _LEFT_WRIST]
    )
    right_visible = all(
        vis[i] >= VISIBILITY_THRESHOLD
        for i in [_RIGHT_SHOULDER, _RIGHT_ELBOW, _RIGHT_WRIST]
    )

    if not left_visible and not right_visible:
        if hysteresis is not None:
            hysteresis.reset()
        return None

    left_angle: Optional[float] = None
    right_angle: Optional[float] = None

    if left_visible:
        left_angle = _calculate_angle(
            _to_pixel(lm[_LEFT_SHOULDER], frame_width, frame_height),
            _to_pixel(lm[_LEFT_ELBOW], frame_width, frame_height),
            _to_pixel(lm[_LEFT_WRIST], frame_width, frame_height),
        )
    if right_visible:
        right_angle = _calculate_angle(
            _to_pixel(lm[_RIGHT_SHOULDER], frame_width, frame_height),
            _to_pixel(lm[_RIGHT_ELBOW], frame_width, frame_height),
            _to_pixel(lm[_RIGHT_WRIST], frame_width, frame_height),
        )

    visible_angles = [a for a in [left_angle, right_angle] if a is not None]
    min_angle = min(visible_angles)

    if hysteresis is not None:
        is_correct = hysteresis.update(min_angle)
    else:
        is_correct = min_angle >= CORRECT_THRESHOLD

    elbow_feedback = (
        "Good: Arms are straight"
        if is_correct
        else f"Straighten your arms ({CORRECT_THRESHOLD - min_angle:.1f}deg short)"
    )

    # ── 어깨 수직 판정 ────────────────────────────────
    shoulder_vertical = _check_shoulder_vertical(lm, frame_width, frame_height, vis)
    if shoulder_vertical is None:
        shoulder_fb = ""
    elif shoulder_vertical:
        shoulder_fb = "Good: Shoulders aligned"
    else:
        shoulder_fb = "Align shoulders over hands"

    # ── 압박 구간 팔꿈치 유지 비율 ───────────────────
    hold_ratio: Optional[float] = None
    hold_feedback = ""

    if elbow_tracker is not None:
        hold_ratio = elbow_tracker.update(in_compression, is_correct)
        if hold_ratio is not None:
            pct = hold_ratio * 100
            if pct >= 80:
                hold_feedback = f"Elbow hold: {pct:.0f}% Good"
            elif pct >= 50:
                hold_feedback = f"Elbow hold: {pct:.0f}% - Try to keep arms straighter"
            else:
                hold_feedback = (
                    f"Elbow hold: {pct:.0f}% - Arms bent too often during compression"
                )

    return PoseEvalResult(
        left_elbow_angle=left_angle if left_angle is not None else -1.0,
        right_elbow_angle=right_angle if right_angle is not None else -1.0,
        is_correct=is_correct,
        feedback=elbow_feedback,
        shoulder_vertical=shoulder_vertical,
        shoulder_feedback=shoulder_fb,
        elbow_hold_ratio=hold_ratio,
        elbow_hold_feedback=hold_feedback,
    )
