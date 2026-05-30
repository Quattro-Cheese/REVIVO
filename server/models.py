from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # 세션 요약 통계 (기존 CSV에서 계산해서 저장)
    avg_bpm = Column(Float, nullable=True)
    avg_depth_cm = Column(Float, nullable=True)
    total_count = Column(Integer, nullable=True)
    posture_correct_ratio = Column(Float, nullable=True)  # 0.0 ~ 1.0
    duration_sec = Column(Float, nullable=True)

    user = relationship("User", back_populates="sessions")
