from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite
from statistics import median
from typing import Optional


@dataclass
class RepResult:
    timestamp_ms: int
    raw_signal: Optional[float]
    baseline: Optional[float]
    depth_now: Optional[float]
    peak_depth: Optional[float]
    count: int
    bpm: Optional[float]
    rate_feedback: str
    metronome_bpm: int
    beat_now: bool

    # [수정] 현재 샘플 기준 변화속도(cm/s)를 추가함.
    # 교수님 피드백: "현재 속도만 고려"가 아니라 압박 깊이 변화량도 봐야 하므로 velocity를 결과로 반환.
    velocity: Optional[float]

    # [수정] 현재 샘플 기준 가속도(cm/s^2)를 추가함.
    # 교수님 피드백: "변화속도(가속도) 반영"을 위해 직전 velocity와 비교해 acceleration 계산.
    acceleration: Optional[float]

    # [수정] 한 회 압박이 끝났을 때 peak_depth가 5~6cm 범위인지 판정한 결과.
    # 기존에는 threshold 한 값만 넘으면 카운트했지만, 이제 CPR 적정 깊이 범위를 따로 피드백함.
    depth_feedback: str


class RepCounter:
    """
    CPR 반복 카운트 / BPM / 메트로놈 타이밍 계산용 독립 모듈

    입력:
    - timestamp_ms: 현재 시각(ms)
    - signal_value: 1차원 신호값
      예) 초음파 distance(cm), 혹은 다른 팀원이 만든 압박 관련 단일 값

    전제:
    - 압박할수록 값이 작아지는 신호라고 가정
      예: 초음파 distance는 누를수록 distance가 줄어듦
    - depth = baseline - current_value 로 계산
    """

    def __init__(
        self,
        calibration_samples: int = 15,
        enter_threshold_cm: float = 4.0,
        release_threshold_cm: float = 1.2,
        refractory_ms: int = 280,
        target_bpm: int = 110,

        # [수정] CPR 적정 압박 깊이를 "하나의 값"이 아니라 "범위"로 둠.
        # 교수님 피드백: 임계값도 한 값이 아닌 범위로 바꿀 것.
        target_depth_min_cm: float = 5.0,
        target_depth_max_cm: float = 6.0,

        # [수정] 순간 튐값 방지를 위한 작은 구간 median filter 크기.
        # 60Hz로 들어오는 초음파 센서값 중 노이즈 하나가 최저점으로 잡히는 문제를 줄임.
        depth_window_size: int = 5,
    ) -> None:
        if calibration_samples <= 0:
            raise ValueError("calibration_samples must be greater than 0")
        if depth_window_size <= 0:
            raise ValueError("depth_window_size must be greater than 0")
        if enter_threshold_cm <= release_threshold_cm:
            raise ValueError("enter_threshold_cm must be greater than release_threshold_cm")
        if refractory_ms < 0:
            raise ValueError("refractory_ms must be greater than or equal to 0")
        if target_bpm <= 0:
            raise ValueError("target_bpm must be greater than 0")
        if target_depth_min_cm <= 0 or target_depth_max_cm <= 0:
            raise ValueError("target depth range must be greater than 0")
        if target_depth_min_cm > target_depth_max_cm:
            raise ValueError("target_depth_min_cm must be less than or equal to target_depth_max_cm")

        self.calibration_samples = calibration_samples
        self.enter_threshold_cm = enter_threshold_cm
        self.release_threshold_cm = release_threshold_cm
        self.refractory_ms = refractory_ms
        self.target_bpm = target_bpm

        # [수정] 적정 깊이 범위 저장.
        self.target_depth_min_cm = target_depth_min_cm
        self.target_depth_max_cm = target_depth_max_cm

        self._baseline_buffer: deque[float] = deque(maxlen=calibration_samples)
        self._baseline: Optional[float] = None
        self._count = 0
        self._compression_times: deque[int] = deque(maxlen=12)
        self._peak_depths: deque[float] = deque(maxlen=6)
        self._in_compression = False

        # [수정] 한 번의 압박 구간 안에서 가장 깊게 눌린 값을 계속 저장.
        # 1초, 2초처럼 듬성듬성 보는 것이 아니라 update가 호출될 때마다 peak를 갱신해서
        # 1.5초에 최저점이 와도 놓치지 않게 함.
        self._current_peak_depth = 0.0
        self._current_peak_time: Optional[int] = None

        self._filtered_depth: Optional[float] = None
        self._last_peak_time: Optional[int] = None
        self._metronome_start_ms: Optional[int] = None

        # [수정] 최근 depth 샘플을 저장해서 median filter에 사용.
        self._depth_window: deque[float] = deque(maxlen=depth_window_size)

        # [수정] 속도/가속도 계산용 이전 상태값.
        self._prev_timestamp_ms: Optional[int] = None
        self._prev_depth: Optional[float] = None
        self._prev_velocity: Optional[float] = None
        self._current_velocity: Optional[float] = None
        self._current_acceleration: Optional[float] = None

        # [수정] 가장 최근에 완료된 압박의 깊이 피드백.
        self._last_depth_feedback = "깊이 수집중"

    def update(self, timestamp_ms: int, signal_value: Optional[float]) -> RepResult:
        if self._metronome_start_ms is None:
            self._metronome_start_ms = timestamp_ms

        if signal_value is not None and not isfinite(signal_value):
            signal_value = None

        if signal_value is None:
            bpm = self._calc_bpm()
            return RepResult(
                timestamp_ms=timestamp_ms,
                raw_signal=None,
                baseline=self._baseline,
                depth_now=None,
                peak_depth=self._latest_peak_depth(),
                count=self._count,
                bpm=bpm,
                rate_feedback=self._rate_feedback(bpm),
                metronome_bpm=self.target_bpm,
                beat_now=self._beat_now(timestamp_ms),
                velocity=self._current_velocity,
                acceleration=self._current_acceleration,
                depth_feedback=self._last_depth_feedback,
            )

        if self._baseline is None:
            self._baseline_buffer.append(signal_value)
            if len(self._baseline_buffer) >= self.calibration_samples:
                self._baseline = float(median(self._baseline_buffer))

            bpm = self._calc_bpm()
            return RepResult(
                timestamp_ms=timestamp_ms,
                raw_signal=signal_value,
                baseline=self._baseline,
                depth_now=None,
                peak_depth=self._latest_peak_depth(),
                count=self._count,
                bpm=bpm,
                rate_feedback="기준값 수집중",
                metronome_bpm=self.target_bpm,
                beat_now=self._beat_now(timestamp_ms),
                velocity=None,
                acceleration=None,
                depth_feedback="기준값 수집중",
            )

        # 압박이 아닐 때 baseline을 천천히 보정
        if not self._in_compression and signal_value >= self._baseline - 0.7:
            self._baseline = (self._baseline * 0.98) + (signal_value * 0.02)

        raw_depth = max(0.0, self._baseline - signal_value)

        # [수정] 60Hz 센서값 중 순간적으로 튀는 값을 줄이기 위해 median filter 적용.
        # 초음파 센서는 갑자기 말도 안 되는 값이 들어올 수 있어서 최저점 오판을 막기 위함.
        self._depth_window.append(raw_depth)
        median_depth = float(median(self._depth_window))

        # 기존 smoothing 유지
        if self._filtered_depth is None:
            self._filtered_depth = median_depth
        else:
            self._filtered_depth = (self._filtered_depth * 0.7) + (median_depth * 0.3)

        # [수정] 현재 깊이 변화속도와 가속도 계산.
        # velocity > 0이면 점점 더 깊게 누르는 중, velocity < 0이면 손을 떼는 중.
        velocity, acceleration = self._calc_motion(timestamp_ms, self._filtered_depth)
        self._current_velocity = velocity
        self._current_acceleration = acceleration

        # 상태 전이는 EMA보다 반응이 빠른 median depth로 판단해 release 지연을 줄인다.
        self._update_state(timestamp_ms, median_depth)

        bpm = self._calc_bpm()
        return RepResult(
            timestamp_ms=timestamp_ms,
            raw_signal=signal_value,
            baseline=self._baseline,
            depth_now=self._filtered_depth,
            peak_depth=self._latest_peak_depth(),
            count=self._count,
            bpm=bpm,
            rate_feedback=self._rate_feedback(bpm),
            metronome_bpm=self.target_bpm,
            beat_now=self._beat_now(timestamp_ms),
            velocity=velocity,
            acceleration=acceleration,
            depth_feedback=self._last_depth_feedback,
        )

    def reset(self) -> None:
        self._baseline_buffer.clear()
        self._baseline = None
        self._count = 0
        self._compression_times.clear()
        self._peak_depths.clear()
        self._in_compression = False
        self._current_peak_depth = 0.0
        self._current_peak_time = None
        self._filtered_depth = None
        self._last_peak_time = None
        self._metronome_start_ms = None

        # [수정] 새로 추가한 상태값도 reset에서 초기화.
        self._depth_window.clear()
        self._prev_timestamp_ms = None
        self._prev_depth = None
        self._prev_velocity = None
        self._current_velocity = None
        self._current_acceleration = None
        self._last_depth_feedback = "깊이 수집중"

    def _calc_motion(self, timestamp_ms: int, depth_now: float) -> tuple[Optional[float], Optional[float]]:
        """
        [수정] 깊이 변화속도와 가속도를 계산하는 함수 추가.
        - velocity 단위: cm/s
        - acceleration 단위: cm/s^2
        """
        if self._prev_timestamp_ms is None or self._prev_depth is None:
            self._prev_timestamp_ms = timestamp_ms
            self._prev_depth = depth_now
            return None, None

        dt = (timestamp_ms - self._prev_timestamp_ms) / 1000.0
        if dt <= 0:
            return self._prev_velocity, self._current_acceleration

        velocity = (depth_now - self._prev_depth) / dt

        acceleration: Optional[float] = None
        if self._prev_velocity is not None:
            acceleration = (velocity - self._prev_velocity) / dt

        self._prev_timestamp_ms = timestamp_ms
        self._prev_depth = depth_now
        self._prev_velocity = velocity

        return velocity, acceleration

    def _update_state(self, timestamp_ms: int, depth_now: float) -> None:
        enough_gap = (
            self._last_peak_time is None
            or (timestamp_ms - self._last_peak_time) >= self.refractory_ms
        )

        if not self._in_compression:
            if depth_now >= self.enter_threshold_cm and enough_gap:
                self._in_compression = True
                self._current_peak_depth = depth_now
                self._current_peak_time = timestamp_ms
        else:
            # [수정] 압박 중에는 매 샘플마다 최고 깊이와 그 시각을 저장.
            # 60Hz로 들어오는 모든 측정값을 보면서 peak를 갱신하므로
            # 중간 시점(예: 1.5초)의 최저 높이도 반영 가능.
            if depth_now > self._current_peak_depth:
                self._current_peak_depth = depth_now
                self._current_peak_time = timestamp_ms

            if depth_now <= self.release_threshold_cm:
                self._in_compression = False

                # 릴리즈까지 확인된 압박만 1회로 인정한다.
                peak_time = self._current_peak_time or timestamp_ms
                peak_depth = self._current_peak_depth
                self._count += 1
                self._compression_times.append(peak_time)
                self._last_peak_time = peak_time
                self._peak_depths.append(peak_depth)
                self._last_depth_feedback = self._depth_feedback(peak_depth)

                self._current_peak_depth = 0.0
                self._current_peak_time = None

    def _depth_feedback(self, peak_depth: float) -> str:
        """
        [수정] 적정 깊이를 단일 임계값이 아닌 범위로 판정.
        """
        if peak_depth < self.target_depth_min_cm:
            return "압박 얕음"
        if peak_depth > self.target_depth_max_cm:
            return "압박 깊음"
        return "깊이 적절"

    def _calc_bpm(self) -> Optional[float]:
        if len(self._compression_times) < 2:
            return None

        times = list(self._compression_times)
        intervals = [times[i] - times[i - 1] for i in range(1, len(times))]
        intervals = [x for x in intervals if x > 0]

        if not intervals:
            return None

        avg_interval = sum(intervals) / len(intervals)
        return 60000.0 / avg_interval

    def _rate_feedback(self, bpm: Optional[float]) -> str:
        if bpm is None:
            return "리듬 수집중"

        if bpm < 100:
            return "속도 느림"
        if bpm > 120:
            return "속도 빠름"
        return "속도 적절"

    def _latest_peak_depth(self) -> Optional[float]:
        if not self._peak_depths:
            return None

        return self._peak_depths[-1]

    def _beat_now(self, timestamp_ms: int) -> bool:
        if self._metronome_start_ms is None:
            return False

        beat_interval = 60000 / self.target_bpm
        elapsed = timestamp_ms - self._metronome_start_ms
        phase = elapsed % beat_interval

        # 70ms 동안만 박자 ON
        return phase < 70


# rep_counter.py 사용할 때 메인에 넣으면 될듯
# from counter.rep_counter import RepCounter
# counter = RepCounter()
# result = counter.update(timestamp_ms=123456, signal_value=10.0)
# print(result.count)
# print(result.bpm)
# print(result.rate_feedback)
# print(result.beat_now)
# print(result.velocity)
# print(result.acceleration)
# print(result.depth_feedback)
