# System Architecture

## Overview

The Construction Site Safety Violation Detection System is organized into
loosely coupled components that communicate via a well-defined API.

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                        │
│                 http://localhost:5173                            │
│                                                                  │
│  ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌─────────────┐  │
│  │  Login   │ │   Dashboard  │ │    Live    │ │  Violations │  │
│  │  Page    │ │   Overview   │ │  Monitor   │ │  History    │  │
│  └──────────┘ └──────────────┘ └────────────┘ └─────────────┘  │
└────────────────────────┬───────────────────────────────────────┘
                         │  REST API (JSON)
                         │  WebSocket (ws://)
┌────────────────────────▼───────────────────────────────────────┐
│                  FastAPI Backend                                 │
│               http://localhost:8000                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Routers                                             │  │
│  │  /api/auth  /api/violations  /api/monitoring  /api/ws    │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │  Video Processing Service (runs in background thread)    │  │
│  │                                                          │  │
│  │  [Frame] → [YOLOv8 Detect] → [DeepSORT Track]           │  │
│  │         → [PPE Associate] → [Violation Rules]            │  │
│  │         → [Alert Engine] → [DB Save] → [WS Broadcast]   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────┬──────────────────────────────────────────────┘
                  │
┌─────────────────▼──────────────────────────────────────────────┐
│                     MongoDB Database                             │
│               mongodb://localhost:27017                          │
│                                                                  │
│  collections: users │ violations │ sessions │ settings           │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Video Input
    │
    ▼ (VideoSource)
Frame Extraction          ← frame_skip, max_width resize
    │
    ▼ (ObjectDetector)
YOLOv8 Detection          ← confidence threshold filter
    │
    ├──► Person detections
    └──► PPE detections (helmet/vest/no-helmet/no-vest)
         │
         ▼ (WorkerTracker)
    DeepSORT Tracking     ← assigns persistent worker IDs
         │
         ▼ (PPEAssociator)
    PPE Association       ← links PPE to correct worker
         │
         ▼ (PoseEstimator)
    Pose Analysis         ← optional; labeled experimental
         │
         ▼ (ViolationEngine)
    Violation Rules       ← persistence check (N frames/seconds)
         │
         ▼ (AlertService)
    Alert Generation      ← cooldown / deduplication
         │
         ├──► MongoDB (persist violation record)
         ├──► Evidence frame saved to disk
         └──► WebSocket broadcast to dashboard
```

## Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| ObjectDetector | `services/detector.py` | YOLOv8 inference, class mapping |
| WorkerTracker | `services/tracker.py` | DeepSORT tracking, ID persistence |
| PPEAssociator | `services/ppe_association.py` | Link PPE to worker by IoU/position |
| PoseEstimator | `services/pose_estimator.py` | MediaPipe keypoint extraction |
| ViolationEngine | `services/violation_engine.py` | Persistence rules, violation records |
| AlertService | `services/alert_service.py` | Cooldown, DB write, WS broadcast |
| VideoProcessor | `services/video_processor.py` | Orchestrates the full pipeline |

## Threading Model

The video processing loop runs in a **separate background thread** (or asyncio task)
so it does not block the FastAPI request/response cycle.

```
Main Thread (FastAPI):     Handles HTTP requests, WebSocket upgrades
Background Thread:         VideoProcessor loop (frame-by-frame)
Shared State:             asyncio.Queue for detections / violations
```

## API Authentication

JWT (JSON Web Token) bearer token authentication:
- Login → POST /api/auth/login → returns access_token
- Protected routes require Authorization: Bearer <token> header
- Tokens expire after ACCESS_TOKEN_EXPIRE_MINUTES

## WebSocket Protocol

Clients connect to: `ws://localhost:8000/api/ws/monitoring`

Server sends JSON messages:

```json
{
  "type": "detection_update",
  "timestamp": "2024-01-01T12:00:00Z",
  "frame_number": 1234,
  "fps": 12.5,
  "workers": [
    {
      "track_id": 1,
      "bbox": [100, 150, 200, 350],
      "confidence": 0.87,
      "ppe_status": {
        "helmet": "missing",
        "vest": "present"
      }
    }
  ],
  "violations": [
    {
      "id": "abc123",
      "worker_id": 1,
      "type": "MISSING_HELMET",
      "severity": "HIGH",
      "confidence": 0.87,
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ]
}
```
