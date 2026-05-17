from __future__ import annotations

from pathlib import Path
import time
import cv2

from pose.detector import PoseDetector
from pose.evaluator import HysteresisJudge, evaluate_pose
from pose.visualizer import draw_eval_result, draw_pose_points
from pose.sensor_reader import UltrasonicReader
from counter.rep_counter import RepCounter

MAX_FRAME_FAILURES = 10


def main() -> None:
    project_root = Path(__file__).resolve().parent
    model_path = project_root / "models" / "pose_landmarker_full.task"

    if not model_path.exists():
        print(f"모델 파일을 찾을 수 없습니다: {model_path}")
        return

    detector = PoseDetector(model_path=str(model_path))
    hysteresis = HysteresisJudge()

    # 아두이노 초음파 센서 연결
    ultrasonic = UltrasonicReader(port="COM12", baudrate=9600)

    # CPR 압박 횟수, 깊이, BPM 계산
    rep_counter = RepCounter(target_bpm=120)

    # TTS 음성 안내
    tts = TTSSpeaker(interval_sec=1.0)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        ultrasonic.close()
        detector.close()
        return

    tts.speak("시작합니다.")

    consecutive_failures = 0

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

            # 자세 추정
            pose_result = detector.detect(frame)
            draw_pose_points(frame, pose_result.image_landmarks)

            eval_result = evaluate_pose(
                pose_result.image_landmarks,
                pose_result.frame_width,
                pose_result.frame_height,
                pose_result.visibilities,
                hysteresis,
            )

            # 초음파 센서 거리값 읽기
            distance_cm = ultrasonic.update()
 ugang-patch-6

            # RepCounter로 압박 깊이, count, BPM 계산
            timestamp_ms = int(time.monotonic() * 1000)

            rep_result = rep_counter.update(
                timestamp_ms=timestamp_ms,
                signal_value=distance_cm,
            )
 main
            rep_result = rep_counter.update(
                timestamp_ms=timestamp_ms,
                signal_value=distance_cm,
            )

            # 자세 인식 성공 여부와 관계없이 초음파/TTS는 동작하게 처리
            if eval_result is not None:
 ugang-patch-6
                posture_correct = eval_result.is_correct
            else:
                posture_correct = True

            # TTS 피드백 문장 생성
            voice_feedback = generate_voice_feedback(
                bpm=rep_result.bpm,
                depth_cm=rep_result.depth_now,
               posture_correct=posture_correct,
            )

            # 디버깅 출력
            print("DIST:", distance_cm)
            print("DEPTH:", rep_result.depth_now)
            print("BPM:", rep_result.bpm)
            print("VOICE:", repr(voice_feedback))

            # TTS 출력
            print("TTS CALL:", repr(voice_feedback))
            tts.speak(voice_feedback)

            # 화면 표시
            if eval_result is not None:
                draw_eval_result(frame, eval_result, distance_cm, rep_result)
            else:
                draw_pose_points(frame, landmarks)

 main
                draw_eval_result(frame, eval_result, distance_cm, rep_result)
            else:
                # 자세 인식이 안 되어도 초음파 관련 값은 화면에 표시
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

            # ESC 키 누르면 종료
            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        ultrasonic.close()
        cap.release()
        detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()