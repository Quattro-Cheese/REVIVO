import math
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..ml.trainer import train_model

router = APIRouter()


def _std(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    return math.sqrt(variance) if variance > 0 else 0.0


@router.get("/stats")
def get_session_stats(db: Session = Depends(get_db)):
    """전체 세션의 지표별 표준편차를 반환 (점수 정규화용)"""
    sessions = db.query(models.Session).all()

    FALLBACK = {"bpm_std": 15.0, "depth_std": 1.5, "posture_std": 0.20, "count_std": 10.0}

    if len(sessions) < 2:
        return {**FALLBACK, "session_count": len(sessions)}

    bpm_std = _std([float(s.avg_bpm) for s in sessions if s.avg_bpm is not None])
    depth_std = _std([float(s.avg_depth_cm) for s in sessions if s.avg_depth_cm is not None])
    posture_std = _std([float(s.posture_correct_ratio) for s in sessions if s.posture_correct_ratio is not None])
    count_std = _std([float(s.total_count) for s in sessions if s.total_count is not None])

    return {
        "bpm_std": max(bpm_std, 1.0),
        "depth_std": max(depth_std, 0.1),
        "posture_std": max(posture_std, 0.01),
        "count_std": max(count_std, 1.0),
        "session_count": len(sessions),
    }


@router.post("/save")
def save_session(
    user_id: int,
    avg_bpm: float,
    avg_depth_cm: float,
    total_count: int,
    posture_correct_ratio: float,
    duration_sec: float,
    db: Session = Depends(get_db),
):
    session = models.Session(
        user_id=user_id,
        avg_bpm=avg_bpm,
        avg_depth_cm=avg_depth_cm,
        total_count=total_count,
        posture_correct_ratio=posture_correct_ratio,
        duration_sec=duration_sec,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    all_sessions = db.query(models.Session).all()
    retrained = train_model(all_sessions)

    return {
        "message": "세션 저장 완료",
        "session_id": session.id,
        "model_retrained": retrained,
    }


@router.get("/detail/{session_id}")
def get_session_detail(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    prev_session = (
        db.query(models.Session)
        .filter(
            models.Session.user_id == session.user_id,
            models.Session.id < session_id,
        )
        .order_by(models.Session.created_at.desc())
        .first()
    )

    return {
        "id": session.id,
        "created_at": session.created_at,
        "avg_bpm": session.avg_bpm,
        "avg_depth_cm": session.avg_depth_cm,
        "total_count": session.total_count,
        "posture_correct_ratio": session.posture_correct_ratio,
        "duration_sec": session.duration_sec,
        "prev_session": (
            {
                "avg_bpm": prev_session.avg_bpm,
                "avg_depth_cm": prev_session.avg_depth_cm,
                "posture_correct_ratio": prev_session.posture_correct_ratio,
            }
            if prev_session
            else None
        ),
    }


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    db.delete(session)
    db.commit()
    return {"message": "세션 삭제 완료", "session_id": session_id}


@router.get("/{user_id}")
def get_sessions(user_id: int, db: Session = Depends(get_db)):
    sessions = (
        db.query(models.Session)
        .filter(models.Session.user_id == user_id)
        .order_by(models.Session.created_at.desc())
        .all()
    )
    return sessions