# 🏗️ Construction Site Safety Violation Detection System

> An AI-powered system that uses computer vision and deep learning to detect PPE violations, track workers, monitor restricted zones, and generate real-time alerts on construction sites.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [System Requirements](#system-requirements)
5. [Quick Start](#quick-start)
6. [Project Structure](#project-structure)
7. [Configuration](#configuration)
8. [Usage](#usage)
9. [API Reference](#api-reference)
10. [Known Limitations](#known-limitations)
11. [License](#license)

---

## Project Overview

This system automatically detects unsafe behavior and missing Personal Protective Equipment (PPE) on construction sites using real-time video feeds. It analyzes video frames, detects workers, tracks them across frames, identifies safety violations, and generates alerts.

**⚠️ Disclaimer:** This AI system is an assistance tool, not a replacement for qualified safety officers. AI predictions can be incorrect due to lighting, occlusion, camera angle, unusual PPE, and model limitations. Human review is required for potentially serious incidents.

---

## Features

- 🎯 **PPE Detection** – Detects helmets and safety vests using YOLOv8
- 👥 **Worker Tracking** – Tracks individual workers with persistent IDs using DeepSORT/ByteTrack
- ⚠️ **Violation Engine** – Configurable persistence rules to avoid false alerts from momentary occlusion
- 🚧 **Restricted Zone Monitoring** – Polygon-based zone configuration
- 📊 **Live Dashboard** – Real-time React dashboard with WebSocket updates
- 🔔 **Alert System** – De-duplicated alerts with cooldown periods
- 📁 **Violation History** – MongoDB-backed searchable violation records
- 📈 **Analytics** – Charts, trends, CSV export

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Object Detection | YOLOv8 (Ultralytics) |
| Multi-Object Tracking | DeepSORT / ByteTrack |
| Pose Estimation | MediaPipe Pose |
| Video Processing | OpenCV |
| Backend API | FastAPI (Python) |
| Database | MongoDB (Motor async driver) |
| Frontend | React + Vite |
| Real-time Updates | WebSocket |

---

## System Requirements

### Minimum (CPU only)
- OS: Windows 10/11, Ubuntu 20.04+, macOS 12+
- CPU: Intel i5 / AMD Ryzen 5 or better
- RAM: 8 GB (16 GB recommended)
- Storage: 10 GB free
- Python: 3.10 or 3.11
- Node.js: 18+

### Recommended (GPU acceleration)
- NVIDIA GPU with 4+ GB VRAM
- CUDA 11.8 or 12.x
- cuDNN compatible version

---

## Quick Start

### Prerequisites
- Python 3.10 or 3.11 installed
- Node.js 18+ installed
- MongoDB installed locally or MongoDB Atlas account
- Git installed

### 1. Clone the repository
```powershell
git clone https://github.com/YOUR_USERNAME/construction-safety-detection.git
cd "construction safety detection"
```

### 2. Set up Python environment
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure environment
```powershell
copy .env.example .env
# Edit .env with your settings
```

### 4. Run basic detection test (Phase 1)
```powershell
# From project root, with venv activated
cd backend
python ..\scripts\test_detection.py
```

### 5. Start backend (Phase 6+)
```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

### 6. Start frontend (Phase 7+)
```powershell
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
construction-safety-detection/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── config.py          # Settings
│   │   ├── api/               # REST endpoints
│   │   ├── services/          # Core AI logic
│   │   ├── models/            # DB models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── database/          # MongoDB connection
│   │   └── utils/             # Helpers
│   ├── tests/                 # Automated tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # React + Vite dashboard
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Dashboard pages
│   │   ├── services/          # API clients
│   │   ├── hooks/             # Custom React hooks
│   │   └── layouts/           # Page layouts
│   └── package.json
├── scripts/                    # Standalone utility scripts
│   ├── test_detection.py      # Phase 1 prototype
│   └── download_sample.py     # Sample video helper
├── datasets/                   # Dataset info (no raw data)
│   └── README.md
├── model_weights/              # Model files (not in git)
│   └── README.md
├── evidence/                   # Saved violation frames
├── docs/                       # Documentation
└── README.md
```

---

## Configuration

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=construction_safety
SECRET_KEY=your-secret-key
DETECTION_CONFIDENCE=0.5
VIOLATION_PERSISTENCE_SECONDS=3
ALERT_COOLDOWN_SECONDS=30
```

---

## Known Limitations

1. **Harness detection** – Reliable fall-protection harness detection requires a dedicated model trained on harness imagery. The current system uses pose estimation as a placeholder indicator only.
2. **Occlusion** – Workers that are heavily occluded may temporarily lose their tracking ID.
3. **Unusual PPE** – Non-standard colored helmets or vests may reduce detection accuracy.
4. **Lighting** – Poor lighting conditions (night, strong backlight) degrade detection confidence.
5. **Camera angle** – Top-down or very oblique camera angles reduce detection accuracy.
6. **FPS** – CPU-only processing achieves 5–15 FPS on 720p video. GPU recommended for real-time.

---

## Responsible AI Notice

This system generates **potential violations** that must be reviewed by a qualified safety officer before any action is taken against a worker. The AI is an assistive tool designed to reduce the cognitive load on safety monitors — it is **not** an automated disciplinary system.

---

## License

This project is developed as a university assignment. See individual model and dataset licenses:
- YOLOv8: AGPL-3.0 (Ultralytics)
- Sample datasets: See `datasets/README.md`
