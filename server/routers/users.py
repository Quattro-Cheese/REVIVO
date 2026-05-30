from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .. import models, auth
from ..database import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="인증 실패")
    except JWTError:
        raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다.")

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user


@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
    }


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
