from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import users, sessions, predict, report

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://cpr-frontend.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(report.router, prefix="/report", tags=["report"])
