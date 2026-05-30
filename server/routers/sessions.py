from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db

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
    return {"message": "세션 저장 완료", "session_id": session.id}


@router.get("/{user_id}")
def get_sessions(user_id: int, db: Session = Depends(get_db)):
    sessions = (
        db.query(models.Session)
        .filter(models.Session.user_id == user_id)
        .order_by(models.Session.created_at.desc())
        .all()
    )
    return sessions
