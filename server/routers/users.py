from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, auth
from ..database import get_db

router = APIRouter()


@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")

    user = models.User(
        username=username, hashed_password=auth.get_password_hash(password)
    )
    db.add(user)
    db.commit()
    return {"message": "회원가입 완료"}


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다."
        )

    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
