# REVIVO

<p align="center">
  <img width="800" alt="revivo" src="https://github.com/user-attachments/assets/9776633e-c2cc-4eed-9e9d-916ede50d965" />
</p>

<p align="center">
  <br>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="license"/></a>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/MediaPipe-0097A7?style=flat-square&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Arduino-00979D?style=flat-square&logo=arduino&logoColor=white"/>
  <img src="https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonaws&logoColor=white"/>
  <br>
</p>

- [한 줄 소개](#한-줄-소개)
- [개발 배경](#개발-배경)
- [주요 기능](#주요-기능)
  - [1. 실시간 자세 분석 & 피드백](#1-실시간-자세-분석--피드백)
  - [2. AI 학습 분석](#2-ai-학습-분석)
- [시스템 아키텍처](#시스템-아키텍처)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [신호 처리 파이프라인](#신호-처리-파이프라인)
- [ML 모델 상세](#ml-모델-상세)
- [실행 방법](#실행-방법)
- [배포](#배포)
- [팀원 소개](#팀원-소개)
- [커밋 컨벤션](#커밋-컨벤션)
- [라이선스](#라이선스)

## 한 줄 소개

> **REVIVO(Revive + O)는** 웹캠과 초음파 센서만으로 CPR 자세를 실시간 분석하고,  
> AI가 개인 맞춤 피드백과 성장 리포트를 제공하는 스마트 심폐소생술 트레이너입니다.

## 개발 배경

대한민국 심정지 환자 생존율은 **약 8.7%** — 선진국 대비 현저히 낮습니다.

심정지 발생 시 **4분 이내 CPR 시행** 여부가 생사를 가르지만, 일반인이 올바른 CPR을 수행하기란 쉽지 않습니다. 기존 CPR 마네킹은 고가이고, 전문 강사 없이는 자세 교정이 어렵습니다. 일회성 교육으로는 정확한 압박 속도(`100~120 BPM`), 깊이(`5~6cm`), 팔꿈치 자세를 몸에 익히기 어렵습니다.

이러한 문제 인식을 바탕으로, **강사 없이도 혼자서 반복 훈련하며 실시간 교정을 받을 수 있는 환경**을 목표로 **REVIVO**를 개발하게 되었습니다.

REVIVO는 웹캠과 저렴한 초음파 센서만으로 **실시간 자세 분석 → 음성 코칭 → ML 기반 집중 영역 예측 → AHA 가이드라인 맞춤 리포트**까지 제공합니다.

## 주요 기능

### 1. 실시간 자세 분석 & 피드백

| 기능                    | 설명                                                        |
| ----------------------- | ----------------------------------------------------------- |
| **압박 속도(BPM)** 측정 | 최근 5회 압박 간격으로 BPM 산출, 100~120 bpm 범위 안내      |
| **압박 깊이(cm)** 측정  | Arduino 초음파 센서로 실시간 깊이 측정 (5~6cm 가이드)       |
| **팔꿈치 자세** 판별    | MediaPipe 관절 랜드마크로 팔꿈치 각도 계산 (163° 이상 유지) |
| **어깨 수직 정렬** 확인 | 손목이 어깨 바로 아래에 위치하는지 검증                     |
| **음성 코칭(TTS)**      | 실시간 교정 메시지를 음성으로 전달                          |
| **메트로놈**            | 시각적 비트 가이드로 올바른 리듬 유지                       |

### 2. AI 학습 분석

| 기능                    | 설명                                                             |
| ----------------------- | ---------------------------------------------------------------- |
| **집중 영역 예측**      | Random Forest 모델이 "속도 / 깊이 / 자세" 중 개선 필요 영역 판별 |
| **자동 재학습**         | 세션이 쌓일수록 모델이 자동으로 재훈련되어 정확도 향상           |
| **RAG 기반 가이드라인** | AHA 2020 CPR 가이드라인에서 맞춤 조언을 검색·제공                |
| **성장 리포트**         | 이전 세션 대비 변화율, 레이더 차트, 트렌드 분석                  |

## 시스템 아키텍처

<p align="center">
  <img src="https://github.com/user-attachments/assets/9634f0d4-7fb0-4b6a-ac2f-3880be683a27" alt="REVIVO Banner" width="800"/>
</p>

## 기술 스택

### Backend

| 기술                                                                                                            | 용도               |
| --------------------------------------------------------------------------------------------------------------- | ------------------ |
| ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)          | REST API 서버      |
| ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) | ORM & 데이터베이스 |
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) | 프로덕션 DB        |
| ![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)            | 인증 토큰          |

### Frontend

| 기술                                                                                                            | 용도           |
| --------------------------------------------------------------------------------------------------------------- | -------------- |
| ![React](https://img.shields.io/badge/React_19-61DAFB?style=flat-square&logo=react&logoColor=black)             | SPA 프레임워크 |
| ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) | 타입 안전성    |
| ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)                   | 빌드 도구      |
| ![Recharts](https://img.shields.io/badge/Recharts-FF6384?style=flat-square&logo=chart.js&logoColor=white)       | 데이터 시각화  |

### AI & Vision

| 기술                                                                                                                  | 용도                             |
| --------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| ![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=flat-square&logo=google&logoColor=white)             | 실시간 포즈 추정 (33개 랜드마크) |
| ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)                   | 영상 처리 & 시각화               |
| ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white) | Random Forest 모델               |
| ![FAISS](https://img.shields.io/badge/FAISS-3B5998?style=flat-square&logo=meta&logoColor=white)                       | 벡터 유사도 검색 (RAG)           |

### Infra & Hardware

| 기술                                                                                                             | 용도                |
| ---------------------------------------------------------------------------------------------------------------- | ------------------- |
| ![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=flat-square&logo=amazonec2&logoColor=white)         | 서버 호스팅         |
| ![AWS RDS](https://img.shields.io/badge/AWS_RDS-527FFF?style=flat-square&logo=amazonrds&logoColor=white)         | 관리형 데이터베이스 |
| ![AWS Bedrock](https://img.shields.io/badge/AWS_Bedrock-232F3E?style=flat-square&logo=amazonaws&logoColor=white) | LLM 기반 AI 피드백  |
| ![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black)              | 백엔드 배포         |
| ![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)              | 프론트엔드 배포     |
| ![Arduino](https://img.shields.io/badge/Arduino-00979D?style=flat-square&logo=arduino&logoColor=white)           | 초음파 센서 펌웨어  |

## 프로젝트 구조

```
Capstone_Design/
├── client/                    # React 프론트엔드
│   └── src/
│       ├── pages/             # Dashboard, Report, Login, Register
│       ├── components/        # PrivateRoute 등 공통 컴포넌트
│       ├── hooks/             # useCurrentUser (인증 훅)
│       ├── api/               # Axios 클라이언트 (JWT 자동 주입)
│       ├── store/             # 상태 관리
│       └── assets/            # 정적 리소스
│
├── server/                    # FastAPI 백엔드
│   ├── routers/               # users, sessions, predict, report API
│   ├── ml/                    # ML 모델 (rf_model, scaler, feature_names)
│   ├── rag/                   # FAISS 인덱스 + AHA 가이드라인 청크
│   ├── models.py              # SQLAlchemy ORM (User, Session)
│   ├── schemas.py             # Pydantic 스키마
│   ├── auth.py                # JWT 인증
│   └── database.py            # DB 연결 설정
│
├── pose/                      # 실시간 CPR 분석 모듈
│   ├── app.py                 # 메인 실행 진입점
│   ├── detector.py            # MediaPipe 포즈 감지
│   ├── evaluator.py           # 자세·BPM·깊이 평가
│   ├── sensor_reader.py       # Arduino 시리얼 통신
│   ├── tts_speaker.py         # 음성 피드백
│   ├── metronome_window.py    # 시각적 메트로놈
│   ├── feedback_generator.py  # 피드백 메시지 생성
│   ├── visualizer.py          # OpenCV 시각화 오버레이
│   ├── models/                # MediaPipe 모델 파일
│   └── logs/                  # 세션 CSV 로그
│
├── counter/                   # 압박 횟수 카운터 모듈
│   └── rep_counter.py         # 히스테리시스 기반 상태 머신
│
├── arduino/                   # 하드웨어 펌웨어
│   └── ultrasonic_depth.ino   # HC-SR04 초음파 센서
│
├── .github/                   # Issue & PR 템플릿
├── render.yaml                # Render 배포 설정
├── vercel.json                # Vercel SPA 라우팅
├── requirements.txt           # Python 의존성
└── seed_dummy.py              # 테스트용 더미 데이터 생성
```

## 신호 처리 파이프라인

REVIVO의 핵심은 **노이즈에 강한 실시간 신호 처리**입니다.

```
초음파 원시값 (60Hz)
      │
      ▼
  [베이스라인 캘리브레이션]   ← 최초 15회 측정값의 중앙값
      │
      ▼
  [메디안 필터 (5-sample)]   ← 스파이크 노이즈 제거
      │
      ▼
  [EMA 스무딩 (α=0.3)]      ← 지수이동평균으로 부드러운 곡선
      │
      ▼
  [히스테리시스 상태 머신]    ← 진입 4.0cm / 해제 2.0cm / 불응기 280ms
      │
      ▼
  횟수 카운트 + BPM 계산 + 깊이 판정
```

## ML 모델 상세

### Feature Engineering

세션 데이터에서 **7개 특징**을 추출하여 학습합니다.

| Feature             | 설명                   |
| ------------------- | ---------------------- |
| `avg_bpm`           | 평균 압박 속도         |
| `bpm_variance`      | BPM 분산 (리듬 안정성) |
| `avg_depth_cm`      | 평균 압박 깊이         |
| `depth_too_shallow` | 깊이 < 5cm 여부        |
| `depth_too_deep`    | 깊이 > 6cm 여부        |
| `posture_incorrect` | 자세 부정확 비율       |
| `session_count`     | 누적 훈련 횟수         |

### 레이블 생성 (비지도 규칙 기반)

| Label | 조건                         | 의미               |
| ----- | ---------------------------- | ------------------ |
| 0     | BPM ∉ [100, 120] & 높은 분산 | **속도** 개선 필요 |
| 1     | 깊이 < 5cm 또는 > 6cm        | **깊이** 개선 필요 |
| 2     | 자세 정확도 < 70%            | **자세** 개선 필요 |
| 3     | 모든 지표 양호               | **Good!**          |

## 실행 방법

### 사전 준비

- Python 3.11+
- Node.js 18+
- Arduino Uno + HC-SR04 초음파 센서
- 웹캠

### 1. 백엔드 서버

```bash
pip install -r requirements.txt
uvicorn server.main:app --reload --port 8000
```

### 2. 프론트엔드

```bash
cd client
npm install
npm run dev
```

### 3. CPR 분석 모듈

```bash
pip install -r pose/requirements.txt
python pose/app.py
```

### 4. 환경 변수

```bash
# 프론트엔드 (.env)
VITE_API_URL=http://localhost:8000

# 백엔드 (.env)
DATABASE_URL=sqlite:///./cpr.db   # 또는 PostgreSQL URL
USE_RAG=true
```

## 배포

| 서비스      | 플랫폼 | URL                                     |
| ----------- | ------ | --------------------------------------- |
| Backend API | Render | `https://cpr-backend-vjpr.onrender.com` |
| Frontend    | Vercel | `https://cpr-frontend.vercel.app`       |

|                                                   김윤지                                                   |                                              정유경                                              |                                            김윤기                                            |                                                안아름                                                |
| :--------------------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------: |
| <a href="https://github.com/yooncandooit"><img src="https://github.com/yooncandooit.png" width="120"/></a> | <a href="https://github.com/ugang04"><img src="https://github.com/ugang04.png" width="120"/></a> | <a href="https://github.com/62-62"><img src="https://github.com/62-62.png" width="120"/></a> | <a href="https://github.com/arumicube"><img src="https://github.com/arumicube.png" width="120"/></a> |
|                                            AI / Web Full-Stack                                             |                                      Embedded / Core Logic                                       |                                 Algorithm / Data Processing                                  |                                         Computer Vision / PM                                         |
|                                 [GitHub](https://github.com/yooncandooit)                                  |                               [GitHub](https://github.com/ugang04)                               |                              [GitHub](https://github.com/62-62)                              |                                [GitHub](https://github.com/arumicube)                                |

### 팀원별 상세 수행 역할

- 김윤지 (AI / Web Full-Stack)
  - 웹 서비스 및 인프라 구축: 풀스택 개발 환경 세팅, SPA 라우팅 오류 수정, 세션 관리 기능 구현 및 DB 연동
  - 경량화 AI 적용: RAG 모델 최적화 및 인덱스 재빌드를 통한 서버 성능 개선

- 정유경 (Embedded / Core Logic)
  - 하드웨어 연동: 초음파 센서의 시리얼 통신(Serial Reader) 구현 및 BPM·압박 깊이 계산 로직을 메인 애플리케이션에 연동
  - 실시간 피드백 시스템: TTS 음성 피드백 기능 개발 및 CPR 피드백 우선순위 로직 수정, 세션 CSV 데이터 저장 추가

- 김윤기 (Algorithm / Data Processing)
  - 데이터 정제 및 보정: 초음파 거리(Depth) 데이터의 정수 변환 및 튀는 값(노이즈) 필터링 알고리즘 설계
  - 판단 로직 안정화: 압박 해제 임계값(release_threshold) 세부 조정 및 CPR 반복 카운터 로직(RepCounter) 모듈 최적화

- 안아름 (Computer Vision / PM)
  - 초기 비전·하드웨어 기반 구축: MediaPipe Pose 모듈 세팅 및 연동, 초음파 센서 압박 깊이 측정·LED 피드백 구현, Pose Estimation 로직 작성
  - 비전 로직 설계: MediaPipe Pose 기반 핵심 커스텀 비전 로직 설계 및 팀 개발 기여 코드 리뷰

> Quattro Cheese | 동국대학교 캡스톤 디자인

## 커밋 컨벤션

```
[Type] 설명

[Feat]     새로운 기능 추가
[Fix]      버그 수정
[Refactor] 코드 리팩토링
[Chore]    빌드·설정·패키지 변경
[Docs]     문서 작성 / 수정
[Update]   기존 기능 개선
[Add]      파일·리소스 추가
```

## 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.
