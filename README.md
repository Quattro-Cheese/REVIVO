# REVIVO

<p align="center">
  <img width="800" alt="revivo" src="https://github.com/user-attachments/assets/9776633e-c2cc-4eed-9e9d-916ede50d965" />
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="license"/></a>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/MediaPipe-0097A7?style=flat-square&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Arduino-00979D?style=flat-square&logo=arduino&logoColor=white"/>
  <img src="https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonaws&logoColor=white"/>
</p>

---

- [Introduction](#introduction)
- [Background](#background)
- [Key Features](#key-features)
  - [1. Real-time Posture Analysis & Feedback](#1-real-time-posture-analysis--feedback)
  - [2. AI Learning Analytics](#2-ai-learning-analytics)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Signal Processing Pipeline](#signal-processing-pipeline)
- [ML Model Details](#ml-model-details)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [Team Members](#team-members)
- [Commit Convention](#commit-convention)
- [License](#license)

---

## Introduction

> **REVIVO (Revive + O)** is a smart CPR trainer that analyzes chest compression posture in real time using only a webcam and ultrasonic sensor, delivering AI-powered personalized feedback and progress reports.

---

## Background

South Korea's cardiac arrest survival rate stands at approximately **8.7%** - significantly lower than other developed nations.

While performing CPR within **4 minutes** of cardiac arrest is critical to survival, it is difficult for the general public to perform it correctly. Conventional CPR mannequins are expensive, and posture correction without a professional instructor is challenging. A one-time training session is rarely enough to internalize the correct compression rate (`100–120 BPM`), depth (`5–6 cm`), and elbow posture.

With this problem in mind, we developed **REVIVO** - a platform designed to enable **solo, repetitive practice with real-time correction, without the need for an instructor**.

REVIVO delivers end-to-end support using only a webcam and a low-cost ultrasonic sensor:
**real-time posture analysis → voice coaching → ML-based focus area prediction → AHA guideline-based personalized reports**

---

## Key Features

### 1. Real-time Posture Analysis & Feedback

| Feature | Description |
|--------|-------------|
| **Compression Rate (BPM)** | Calculates BPM from the last 5 compression intervals; guides toward 100–120 BPM |
| **Compression Depth (cm)** | Measures real-time depth via Arduino ultrasonic sensor (target: 5–6 cm) |
| **Elbow Posture Detection** | Calculates elbow angle using MediaPipe joint landmarks (target: ≥163°) |
| **Shoulder Vertical Alignment** | Verifies wrist is positioned directly below the shoulder |
| **Voice Coaching (TTS)** | Delivers real-time corrective messages via speech |
| **Metronome** | Visual beat guide to help maintain correct rhythm |

### 2. AI Learning Analytics

| Feature | Description |
|--------|-------------|
| **Focus Area Prediction** | Random Forest model identifies which area needs improvement: speed / depth / posture |
| **Auto Retraining** | Model automatically retrains as sessions accumulate, improving accuracy over time |
| **RAG-based Guidelines** | Retrieves personalized advice from the AHA 2020 CPR Guidelines |
| **Progress Report** | Session-over-session change rate, radar chart, and trend analysis |

---

## System Architecture

<p align="center">
  <img src="https://github.com/user-attachments/assets/9634f0d4-7fb0-4b6a-ac2f-3880be683a27" alt="REVIVO Architecture" width="800"/>
</p>

---

## Tech Stack

### Backend

| Tech | Usage |
|------|-------|
| ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) | REST API server |
| ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) | ORM & database management |
| ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) | Production database |
| ![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white) | Authentication tokens |

### Frontend

| Tech | Usage |
|------|-------|
| ![React](https://img.shields.io/badge/React_19-61DAFB?style=flat-square&logo=react&logoColor=black) | SPA framework |
| ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) | Type safety |
| ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white) | Build tool |
| ![Recharts](https://img.shields.io/badge/Recharts-FF6384?style=flat-square&logo=chart.js&logoColor=white) | Data visualization |

### AI & Vision

| Tech | Usage |
|------|-------|
| ![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=flat-square&logo=google&logoColor=white) | Real-time pose estimation (33 landmarks) |
| ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white) | Video processing & visualization |
| ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white) | Random Forest model |
| ![FAISS](https://img.shields.io/badge/FAISS-3B5998?style=flat-square&logo=meta&logoColor=white) | Vector similarity search (RAG) |

### Infrastructure & Hardware

| Tech | Usage |
|------|-------|
| ![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=flat-square&logo=amazonec2&logoColor=white) | Server hosting |
| ![AWS RDS](https://img.shields.io/badge/AWS_RDS-527FFF?style=flat-square&logo=amazonrds&logoColor=white) | Managed database |
| ![AWS Bedrock](https://img.shields.io/badge/AWS_Bedrock-232F3E?style=flat-square&logo=amazonaws&logoColor=white) | LLM-based AI feedback |
| ![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black) | Backend deployment |
| ![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white) | Frontend deployment |
| ![Arduino](https://img.shields.io/badge/Arduino-00979D?style=flat-square&logo=arduino&logoColor=white) | Ultrasonic sensor firmware |

---

## Project Structure

```
Capstone_Design/
├── client/                    # React frontend
│   └── src/
│       ├── pages/             # Dashboard, Report, Login, Register
│       ├── components/        # Shared components (e.g. PrivateRoute)
│       ├── hooks/             # useCurrentUser (auth hook)
│       ├── api/               # Axios client (auto JWT injection)
│       ├── store/             # State management
│       └── assets/            # Static resources
│
├── server/                    # FastAPI backend
│   ├── routers/               # users, sessions, predict, report API
│   ├── ml/                    # ML model (rf_model, scaler, feature_names)
│   ├── rag/                   # FAISS index + AHA guideline chunks
│   ├── models.py              # SQLAlchemy ORM (User, Session)
│   ├── schemas.py             # Pydantic schemas
│   ├── auth.py                # JWT authentication
│   └── database.py            # DB connection setup
│
├── pose/                      # Real-time CPR analysis module
│   ├── app.py                 # Main entry point
│   ├── detector.py            # MediaPipe pose detection
│   ├── evaluator.py           # Posture / BPM / depth evaluation
│   ├── sensor_reader.py       # Arduino serial communication
│   ├── tts_speaker.py         # Voice feedback
│   ├── metronome_window.py    # Visual metronome
│   ├── feedback_generator.py  # Feedback message generation
│   ├── visualizer.py          # OpenCV visualization overlay
│   ├── models/                # MediaPipe model files
│   └── logs/                  # Session CSV logs
│
├── counter/                   # Compression counter module
│   └── rep_counter.py         # Hysteresis-based state machine
│
├── arduino/                   # Hardware firmware
│   └── ultrasonic_depth.ino   # HC-SR04 ultrasonic sensor
│
├── .github/                   # Issue & PR templates
├── render.yaml                # Render deployment config
├── vercel.json                # Vercel SPA routing
├── requirements.txt           # Python dependencies
└── seed_dummy.py              # Dummy data generator for testing
```

---

## Signal Processing Pipeline

The core of REVIVO is its **noise-resilient real-time signal processing**.

```
Raw ultrasonic signal (60Hz)
        │
        ▼
  [Baseline Calibration]      ← Median of first 15 measurements
        │
        ▼
  [Median Filter (5-sample)]  ← Spike noise removal
        │
        ▼
  [EMA Smoothing (α=0.3)]     ← Exponential moving average for smooth curve
        │
        ▼
  [Hysteresis State Machine]  ← Entry: 4.0cm / Release: 2.0cm / Refractory: 280ms
        │
        ▼
  Rep Count + BPM Calculation + Depth Evaluation
```

---

## ML Model Details

### Feature Engineering

**7 features** are extracted from session data for model training:

| Feature | Description |
|---------|-------------|
| `avg_bpm` | Average compression rate |
| `bpm_variance` | BPM variance (rhythm stability) |
| `avg_depth_cm` | Average compression depth |
| `depth_too_shallow` | Depth < 5 cm flag |
| `depth_too_deep` | Depth > 6 cm flag |
| `posture_incorrect` | Ratio of incorrect posture frames |
| `session_count` | Cumulative training session count |

### Label Generation (Rule-based, Unsupervised)

| Label | Condition | Meaning |
|-------|-----------|---------|
| 0 | BPM ∉ [100, 120] & high variance | Improve **Rate** |
| 1 | Depth < 5 cm or > 6 cm | Improve **Depth** |
| 2 | Posture accuracy < 70% | Improve **Posture** |
| 3 | All metrics within range | **Good!** |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Arduino Uno + HC-SR04 ultrasonic sensor
- Webcam

### 1. Backend Server

```bash
pip install -r requirements.txt
uvicorn server.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd client
npm install
npm run dev
```

### 3. CPR Analysis Module

```bash
pip install -r pose/requirements.txt
python pose/app.py
```

### 4. Environment Variables

```bash
# Frontend (.env)
VITE_API_URL=http://localhost:8000

# Backend (.env)
DATABASE_URL=sqlite:///./cpr.db   # or PostgreSQL URL
USE_RAG=true
```

---

## Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Backend API | Render | `https://cpr-backend-vjpr.onrender.com` |
| Frontend | Vercel | `https://cpr-frontend.vercel.app` |

---

## Team Members

|  |  |  |  |
|:---:|:---:|:---:|:---:|
| <a href="https://github.com/yooncandooit"><img src="https://github.com/yooncandooit.png" width="120"/></a> | <a href="https://github.com/ugang04"><img src="https://github.com/ugang04.png" width="120"/></a> | <a href="https://github.com/62-62"><img src="https://github.com/62-62.png" width="120"/></a> | <a href="https://github.com/arumicube"><img src="https://github.com/arumicube.png" width="120"/></a> |
| **Yoonji Kim** | **Yukyung Jeong** | **Yungi Kim** | **Aryum Ahn** |
| AI / Web Full-Stack | Embedded / Core Logic | Algorithm / Data Processing | Computer Vision / PM |
| [GitHub](https://github.com/yooncandooit) | [GitHub](https://github.com/ugang04) | [GitHub](https://github.com/62-62) | [GitHub](https://github.com/arumicube) |

### Responsibilities

| Member | Role Details |
|--------|-------------|
| **Yoonji Kim** | Full-stack web service & infrastructure setup, session management & DB integration, RAG model optimization via index rebuild, CSV compression log analysis for threshold insights |
| **Yukyung Jeong** | Hardware integration (Serial Reader for ultrasonic sensor), BPM & depth calculation logic, TTS voice feedback, CPR feedback priority logic, session CSV data storage |
| **Yungi Kim** | Ultrasonic depth data integer conversion & noise filtering algorithm, release threshold fine-tuning, RepCounter module optimization |
| **Aryum Ahn** | MediaPipe Pose module setup & integration, ultrasonic depth measurement & LED feedback, custom vision logic design, code review |

> **Quattro Cheese** | Dongguk University

---

## Commit Convention

```
[Feat]     Add new feature
[Fix]      Bug fix
[Refactor] Code refactoring
[Chore]    Build / config / package changes
[Docs]     Documentation
[Update]   Improve existing feature
[Add]      Add files or resources
```

---

## License

This project is licensed under the [MIT License](LICENSE).
