from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import users, sessions

Base.metadata.create_all(bind=engine)  # 테이블 자동 생성

app = FastAPI()

# React에서 접근할 수 있도록 CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React 개발서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])


@app.get("/")
def root():
    return {"message": "CPR Training API"}
