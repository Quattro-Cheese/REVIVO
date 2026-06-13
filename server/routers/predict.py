import math

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
import pickle
import numpy as np
from pathlib import Path

def _safe_float(v) -> float | None:
    if v is None:
        return None
    try:
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return None
      
router = APIRouter()

ML_DIR = Path(__file__).resolve().parent.parent / "ml"

# 서버 시작 시 모델 로드
try:
    rf_model = pickle.load(open(ML_DIR / "rf_model.pkl", "rb"))
    scaler = pickle.load(open(ML_DIR / "scaler.pkl", "rb"))
    feature_names = pickle.load(open(ML_DIR / "feature_names.pkl", "rb"))
    print("✅ 모델 로드 완료:", feature_names)
except Exception as e:
    print("❌ 모델 로드 실패:", e)
    rf_model = None
    scaler = None
    feature_names = None

LABEL_MAP = {
    0: "압박 속도 집중 필요",
    1: "압박 깊이 집중 필요",
    2: "팔꿈치 자세 집중 필요",
    3: "전반적으로 양호합니다",
}


@router.get("/{user_id}")
def predict_focus(user_id: int, db: Session = Depends(get_db)):
    if rf_model is None:
        raise HTTPException(status_code=500, detail="모델이 로드되지 않았습니다.")

    # 해당 유저의 세션 히스토리 조회
    sessions = (
        db.query(models.Session)
        .filter(models.Session.user_id == user_id)
        .order_by(models.Session.created_at.desc())
        .all()
    )

    if not sessions:
        raise HTTPException(status_code=404, detail="세션 기록이 없습니다.")

    latest = sessions[0]
    session_count = len(sessions)

    # BPM 분산 계산 (세션이 2개 이상일 때)
    bpm_list = [s.avg_bpm for s in sessions if s.avg_bpm is not None]
    bpm_variance = float(np.var(bpm_list)) if len(bpm_list) >= 2 else 0.0

    # 깊이 불량 비율 추정 (avg_depth 기준)
    depth_too_shallow = 1.0 if (latest.avg_depth_cm or 0) < 5.0 else 0.0
    depth_too_deep = 1.0 if (latest.avg_depth_cm or 0) > 6.0 else 0.0
    posture_incorrect = 1.0 - (latest.posture_correct_ratio or 0.0)

    features = np.array(
        [
            [
                latest.avg_bpm or 0.0,
                bpm_variance,
                latest.avg_depth_cm or 0.0,
                depth_too_shallow,
                depth_too_deep,
                posture_incorrect,
                session_count,
            ]
        ]
    )

    features_scaled = scaler.transform(features)
    label = int(rf_model.predict(features_scaled)[0])
    proba = rf_model.predict_proba(features_scaled)[0]

    return {
        "user_id": user_id,
        "session_count": session_count,
        "focus": LABEL_MAP[label],
        "label": label,
        "confidence": round(float(max(proba)) * 100, 1),
        "latest_session": {
            "avg_bpm": _safe_float(latest.avg_bpm),
            "avg_depth_cm": _safe_float(latest.avg_depth_cm),
            "total_count": latest.total_count,
            "posture_correct_ratio": _safe_float(latest.posture_correct_ratio),
        },
    }
