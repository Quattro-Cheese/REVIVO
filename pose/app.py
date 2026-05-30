from __future__ import annotations

from pathlib import Path
from datetime import datetime
import csv
import time
import cv2
import requests
import pandas as pd
import os

from dotenv import load_dotenv
from pose.detector import PoseDetector
from pose.evaluator import HysteresisJudge, evaluate_pose
from pose.visualizer import draw_eval_result, draw_pose_points
from pose.sensor_reader import UltrasonicReader
from pose.feedback_generator import generate_voice_feedback
from pose.tts_speaker import TTSSpeaker
from counter.rep_counter import RepCounter
from pose.evaluator import HysteresisJudge, ElbowHoldTracker, evaluate_pose

MAX_FRAME_FAILURES = 10
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def save_session_to_db(
    user_id: int,
    avg_bpm: float,
    avg_depth_cm: float,
    total_count: int,
    posture_correct_ratio: float,
    duration_sec: float,
) -> None:
    try:
        response = requests.post(
            f"{BACKEND_URL}/sessions/save",
            params={
                "user_id": user_id,
                "avg_bpm": avg_bpm,
                "avg_depth_cm": avg_depth_cm,
                "total_count": total_count,
                "posture_correct_ratio": posture_correct_ratio,
                "duration_sec": duration_sec,
            },
        )
        print("세션 저장 완료:", response.json())
    except Exception as e:
        print("세션 저장 실패:", e)


def draw_sensor_values(frame, distance_cm, rep_result) -> None:
    """자세 인식이 실패해도 초음파/압박 관련 값을 화면에 표시한다."""
    y = 30

    if distance_cm is not None:
        cv2.putText(
            frame,
            f"DIST: {distance_cm:.1f} cm",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        y += 30

    if rep_result.depth_now is not None:
        cv2.putText(
            frame,
            f"Depth: {rep_result.depth_now:.1f} cm",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        y += 30

    if rep_result.bpm is not None:
        cv2.putText(
            frame,
            f"BPM: {rep_result.bpm:.1f}",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        y += 30

    cv2.putText(
        frame,
        f"Count: {rep_result.count}",
        (10, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )


def main() -> None:
    project_root = Path(__file__).resolve().parent
    model_path = project_root / "models" / "pose_landmarker_full.task"

    if not model_path.exists():
        print(f"모델 파일을 찾을 수 없습니다: {model_path}")
        return

    # CSV 로그 파일 생성
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    log_path = log_dir / f"cpr_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    log_file = open(log_path, "w", newline="", encoding="utf-8-sig")
    csv_writer = csv.writer(log_file)

    csv_writer.writerow(
        [
            "wall_time",
            "elapsed_ms",
            "timestamp_ms",
            "distance_cm",
            "depth_cm",
            "bpm",
            "count",
            "posture_correct",
            "shoulder_vertical",
            "elbow_hold_ratio",
            "voice_feedback",
        ]
    )

    print(f"CSV 로그 저장 경로: {log_path}")

    detector = PoseDetector(model_path=str(model_path))
    hysteresis = HysteresisJudge()
    elbow_tracker = ElbowHoldTracker()

    ultrasonic = UltrasonicReader(port="COM12", baudrate=9600)
    rep_counter = RepCounter(target_bpm=120)
    tts = TTSSpeaker(interval_sec=1.0)

    cap = cv2.VideoCapture(0)
    rep_result = rep_counter.update(
        timestamp_ms=int(time.monotonic() * 1000), signal_value=None
    )

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        log_file.close()
        ultrasonic.close()
        detector.close()
        return

    tts.speak("시작합니다.")

    consecutive_failures = 0
    start_timestamp_ms = int(time.monotonic() * 1000)

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                consecutive_failures += 1
                if consecutive_failures >= MAX_FRAME_FAILURES:
                    print("카메라 프레임을 읽을 수 없습니다.")
                    break
                continue

            consecutive_failures = 0
            frame = cv2.flip(frame, 1)

            pose_result = detector.detect(frame)
            draw_pose_points(frame, pose_result.image_landmarks)

            eval_result = evaluate_pose(
                pose_result.image_landmarks,
                pose_result.frame_width,
                pose_result.frame_height,
                pose_result.visibilities,
                hysteresis,
                elbow_tracker=elbow_tracker,
                in_compression=rep_result.in_compression,  # RepCounter 내부 상태
            )

            distance_cm = ultrasonic.update()

            timestamp_ms = int(time.monotonic() * 1000)
            elapsed_ms = timestamp_ms - start_timestamp_ms

            rep_result = rep_counter.update(
                timestamp_ms=timestamp_ms,
                signal_value=distance_cm,
            )

            if eval_result is not None:
                posture_correct = eval_result.is_correct
            else:
                posture_correct = True

            voice_feedback = generate_voice_feedback(
                bpm=rep_result.bpm,
                depth_cm=rep_result.peak_depth,
                posture_correct=posture_correct,
            )

            csv_writer.writerow(
                [
                    datetime.now().isoformat(timespec="milliseconds"),
                    elapsed_ms,
                    timestamp_ms,
                    distance_cm,
                    rep_result.depth_now,
                    rep_result.bpm,
                    rep_result.count,
                    posture_correct,
                    eval_result.shoulder_vertical if eval_result else None,
                    eval_result.elbow_hold_ratio if eval_result else None,
                    voice_feedback,
                ]
            )
            log_file.flush()

            print("DIST:", distance_cm)
            print("DEPTH:", rep_result.depth_now)
            print("BPM:", rep_result.bpm)
            print("COUNT:", rep_result.count)
            print("VOICE:", repr(voice_feedback))
            print("TTS CALL:", repr(voice_feedback))
            tts.speak(voice_feedback)

            if eval_result is not None:
                draw_eval_result(frame, eval_result, distance_cm, rep_result)
            else:
                draw_sensor_values(frame, distance_cm, rep_result)

            cv2.putText(
                frame,
                "Tip: Position camera so arm is fully visible from the side",
                (10, frame.shape[0] - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1,
            )

            cv2.imshow("CPR Pose Estimation", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        # 리소스 정리
        log_file.close()
        ultrasonic.close()
        cap.release()
        detector.close()
        cv2.destroyAllWindows()

        # 세션 통계 계산 및 DB 저장
        elapsed_total = (int(time.monotonic() * 1000) - start_timestamp_ms) / 1000.0

        try:
            df = pd.read_csv(log_path)

            avg_bpm = float(df["bpm"].dropna().mean()) if "bpm" in df.columns else 0.0
            avg_depth = (
                float(df["depth_cm"].dropna().mean())
                if "depth_cm" in df.columns
                else 0.0
            )
            total_count = int(df["count"].max()) if "count" in df.columns else 0
            posture_ratio = (
                float(df["posture_correct"].sum() / len(df))
                if "posture_correct" in df.columns and len(df) > 0
                else 0.0
            )

            save_session_to_db(
                user_id=1,  # 임시: 나중에 로그인 연동 후 실제 user_id로 교체
                avg_bpm=round(avg_bpm, 2),
                avg_depth_cm=round(avg_depth, 2),
                total_count=total_count,
                posture_correct_ratio=round(posture_ratio, 2),
                duration_sec=round(elapsed_total, 2),
            )
        except Exception as e:
            print("세션 통계 계산 실패:", e)


if __name__ == "__main__":
    main()
