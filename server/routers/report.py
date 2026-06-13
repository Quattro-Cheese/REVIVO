import math

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..rag.retriever import GuidelineRetriever
import pickle
import numpy as np
from pathlib import Path
import os

def _safe_float(v) -> float | None:
    """NaN/Inf를 None으로 변환해 JSON 직렬화 오류 방지"""
    if v is None:
        return None
    try:
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return None
      
router = APIRouter()

ML_DIR = Path(__file__).resolve().parent.parent / "ml"

LABEL_MAP = {
    0: "압박 속도 집중 필요",
    1: "압박 깊이 집중 필요",
    2: "팔꿈치 자세 집중 필요",
    3: "전반적으로 양호합니다",
}

QUERY_MAP = {
    0: "CPR compression rate 100 to 120 per minute",
    1: "CPR compression depth 5 to 6 cm",
    2: "CPR elbow posture locked arms technique",
    3: "CPR good performance guidelines",
}

USE_RAG = os.getenv("USE_RAG", "false").lower() == "true"


@router.get("/{user_id}")
def generate_report(user_id: int, db: Session = Depends(get_db)):
    # 세션 히스토리 조회
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

    # 모델로 집중 항목 예측
    try:
        rf_model = pickle.load(open(ML_DIR / "rf_model.pkl", "rb"))
        scaler = pickle.load(open(ML_DIR / "scaler.pkl", "rb"))

        bpm_list = [s.avg_bpm for s in sessions if s.avg_bpm is not None]
        bpm_variance = float(np.var(bpm_list)) if len(bpm_list) >= 2 else 0.0
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
    except Exception as e:
        label = 3

    focus = LABEL_MAP[label]

    # RAG로 관련 가이드라인 검색
    if USE_RAG:
        retriever = GuidelineRetriever()
        guideline_chunks = retriever.search(QUERY_MAP[label], top_k=2)
    else:
        guideline_chunks = [
            "AHA 2020 가이드라인: 성인 CPR 시 분당 100~120회 속도로 5~6cm 깊이로 압박합니다.",
            "팔꿈치를 곧게 펴고 체중을 이용해 압박하세요.",
        ]

    # 이전 세션과 비교
    trend = ""
    if len(sessions) >= 2:
        prev = sessions[1]
        bpm_diff = (latest.avg_bpm or 0) - (prev.avg_bpm or 0)
        depth_diff = (latest.avg_depth_cm or 0) - (prev.avg_depth_cm or 0)
        trend = f"BPM {'▲' if bpm_diff > 0 else '▼'} {abs(bpm_diff):.1f}, 깊이 {'▲' if depth_diff > 0 else '▼'} {abs(depth_diff):.1f}cm"

    return {
        "user_id": user_id,
        "session_count": session_count,
        "focus": focus,
        "trend": trend,
        "latest_session": {
            "avg_bpm": _safe_float(latest.avg_bpm),
            "avg_depth_cm": _safe_float(latest.avg_depth_cm),
            "total_count": latest.total_count,
            "posture_correct_ratio": _safe_float(latest.posture_correct_ratio),
            "duration_sec": _safe_float(latest.duration_sec),
        },
        "guideline": guideline_chunks,
    }
