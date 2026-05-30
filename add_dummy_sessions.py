import requests

BASE_URL = "http://localhost:8000"

# user_id=1 에 다양한 세션 추가
sessions = [
    {
        "avg_bpm": 95.0,
        "avg_depth_cm": 4.2,
        "total_count": 20,
        "posture_correct_ratio": 0.6,
        "duration_sec": 60,
    },
    {
        "avg_bpm": 102.0,
        "avg_depth_cm": 4.8,
        "total_count": 25,
        "posture_correct_ratio": 0.7,
        "duration_sec": 65,
    },
    {
        "avg_bpm": 108.0,
        "avg_depth_cm": 5.2,
        "total_count": 28,
        "posture_correct_ratio": 0.78,
        "duration_sec": 70,
    },
    {
        "avg_bpm": 112.0,
        "avg_depth_cm": 5.5,
        "total_count": 32,
        "posture_correct_ratio": 0.85,
        "duration_sec": 72,
    },
    {
        "avg_bpm": 115.0,
        "avg_depth_cm": 5.7,
        "total_count": 35,
        "posture_correct_ratio": 0.90,
        "duration_sec": 75,
    },
]

for i, s in enumerate(sessions):
    res = requests.post(f"{BASE_URL}/sessions/save", params={"user_id": 1, **s})
    print(f"세션 {i+1} 저장:", res.json())
