from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite로 먼저 시작 (파일 하나로 동작, 설치 불필요)
DATABASE_URL = "sqlite:///./cpr.db"

# 나중에 PostgreSQL로 바꿀 때는 아래로 교체
# DATABASE_URL = "postgresql://postgres:비밀번호@localhost:5432/cpr_db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
