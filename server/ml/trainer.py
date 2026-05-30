# 세션이 쌓일 때마다 자동으로 모델 재학습

import pickle
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

ML_DIR = Path(__file__).resolve().parent


def extract_features(sessions: list) -> tuple:
    X, y = [], []

    for i, s in enumerate(sessions):
        if s.avg_bpm is None:
            continue

        bpm_list = [prev.avg_bpm for prev in sessions[: i + 1] if prev.avg_bpm]
        bpm_variance = float(np.var(bpm_list)) if len(bpm_list) >= 2 else 0.0
        depth_too_shallow = 1.0 if (s.avg_depth_cm or 0) < 5.0 else 0.0
        depth_too_deep = 1.0 if (s.avg_depth_cm or 0) > 6.0 else 0.0
        posture_incorrect = 1.0 - (s.posture_correct_ratio or 0.0)

        # 레이블 자동 생성
        if not (100 <= (s.avg_bpm or 0) <= 120) and bpm_variance > 12:
            label = 0  # 속도
        elif depth_too_shallow > 0.3 or depth_too_deep > 0.2:
            label = 1  # 깊이
        elif posture_incorrect > 0.3:
            label = 2  # 자세
        else:
            label = 3  # 양호

        X.append(
            [
                s.avg_bpm or 0.0,
                bpm_variance,
                s.avg_depth_cm or 0.0,
                depth_too_shallow,
                depth_too_deep,
                posture_incorrect,
                i + 1,
            ]
        )
        y.append(label)

    return np.array(X), np.array(y)


def train_model(sessions: list) -> bool:
    """세션 데이터로 모델을 학습하고 저장. 성공 여부 반환."""
    if len(sessions) < 1:
        return False  # 데이터가 너무 적으면 학습 안 함

    X, y = extract_features(sessions)
    if len(X) < 3:
        return False

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_scaled, y)

    pickle.dump(model, open(ML_DIR / "rf_model.pkl", "wb"))
    pickle.dump(scaler, open(ML_DIR / "scaler.pkl", "wb"))

    print(f"✅ 모델 재학습 완료: {len(sessions)}개 세션 사용")
    return True
