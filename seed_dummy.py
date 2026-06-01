"""
배포 서버에 test 계정 더미 세션 데이터를 삽입하는 스크립트
"""

import requests
import random
import time
from datetime import datetime, timedelta

BASE_URL = "https://cpr-backend-vjpr.onrender.com"
USERNAME = "test"
PASSWORD = "test"


def register():
    r = requests.post(
        f"{BASE_URL}/users/register",
        params={"username": USERNAME, "password": PASSWORD},
    )
    if r.status_code == 200:
        print("회원가입 완료")
    elif r.status_code == 400:
        print("이미 존재하는 계정 (계속 진행)")
    else:
        print(f"register 오류: {r.status_code} {r.text}")


def login():
    r = requests.post(
        f"{BASE_URL}/users/login", data={"username": USERNAME, "password": PASSWORD}
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    print(f"로그인 성공, token: {token[:20]}...")
    return token


def save_session(token: str, **kwargs):
    r = requests.post(
        f"{BASE_URL}/sessions/save",
        params=kwargs,
        headers={"Authorization": f"Bearer {token}"},
    )
    if r.status_code == 200:
        sid = r.json().get("session_id")
        print(f"  세션 저장 완료 (id={sid})")
    else:
        print(f"  세션 저장 실패: {r.status_code} {r.text}")


def get_user_id(token: str) -> int:
    r = requests.get(
        f"{BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    r.raise_for_status()
    return r.json()["id"]


def rand_bpm():
    """100~120 정상 범위 위주, 간혹 이탈"""
    roll = random.random()
    if roll < 0.6:
        return round(random.uniform(100, 120), 1)
    elif roll < 0.8:
        return round(random.uniform(85, 99), 1)
    else:
        return round(random.uniform(121, 140), 1)


def rand_depth():
    """5~6 cm 정상 범위 위주, 간혹 이탈"""
    roll = random.random()
    if roll < 0.6:
        return round(random.uniform(5.0, 6.0), 2)
    elif roll < 0.8:
        return round(random.uniform(3.5, 4.9), 2)
    else:
        return round(random.uniform(6.1, 7.5), 2)


def rand_posture():
    """0.5 ~ 1.0"""
    return round(random.uniform(0.5, 1.0), 2)


def rand_count():
    """25 ~ 40"""
    return random.randint(25, 40)


def rand_duration():
    """20 ~ 60초"""
    return round(random.uniform(20, 60), 1)


def main():
    register()
    token = login()
    user_id = get_user_id(token)
    print(f"user_id: {user_id}")

    NUM_SESSIONS = 30
    print(f"\n{NUM_SESSIONS}개 더미 세션 삽입 시작...\n")

    for i in range(NUM_SESSIONS):
        save_session(
            token,
            user_id=user_id,
            avg_bpm=rand_bpm(),
            avg_depth_cm=rand_depth(),
            total_count=rand_count(),
            posture_correct_ratio=rand_posture(),
            duration_sec=rand_duration(),
        )
        time.sleep(0.3)

    print(f"\n완료! {NUM_SESSIONS}개 세션 삽입됨")


if __name__ == "__main__":
    main()
