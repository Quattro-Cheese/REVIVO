from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..ml.trainer import train_model

router = APIRouter()


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


@router.get("/{user_id}")
def get_sessions(user_id: int, db: Session = Depends(get_db)):
    sessions = (
        db.query(models.Session)
        .filter(models.Session.user_id == user_id)
        .order_by(models.Session.created_at.desc())
        .all()
    )
    return sessions


# 세션 단건 조회
@router.get("/detail/{session_id}")
def get_session_detail(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    # 같은 유저의 이전 세션 조회 (비교용)
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
