# Setup Guide

## Prerequisites

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.10 or 3.11 | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| Git | Latest | https://git-scm.com/ |
| MongoDB | 7.0+ | https://www.mongodb.com/try/download/community |
| VS Code | Latest | https://code.visualstudio.com/ |

## VS Code Extensions (Recommended)

Install these from the VS Code Extensions marketplace:
- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **ES7+ React/Redux/React-Native snippets**
- **Prettier** (code formatter)
- **MongoDB for VS Code**
- **Thunder Client** (API testing, alternative to Postman)

---

## Step 1 — Clone / Open the Project

```powershell
# If you have git:
git clone https://github.com/YOUR_USERNAME/construction-safety-detection.git
cd "construction safety detection"

# Or open the existing folder in VS Code:
code "C:\Users\YourName\construction safety detection"
```

---

## Step 2 — Python Virtual Environment

Open a **PowerShell** terminal in VS Code (`Ctrl+`` ` or Terminal → New Terminal`).

```powershell
# Navigate to the backend folder
cd backend

# Create the virtual environment
python -m venv venv

# Activate it (you must do this every time you open a new terminal)
.\venv\Scripts\Activate.ps1

# If you get a security error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify activation — you should see (venv) in your prompt
```

---

## Step 3 — Install Python Dependencies

```powershell
# Make sure venv is activated, then:
pip install --upgrade pip
pip install -r requirements.txt

# This will install (among others):
#   ultralytics  (YOLOv8)
#   opencv-python
#   fastapi
#   motor        (async MongoDB)
#   mediapipe
```

**⏱️  First install takes 5–10 minutes** because it downloads PyTorch and OpenCV.

---

## Step 4 — Environment Configuration

```powershell
# Copy the example file
copy .env.example .env

# Open .env in VS Code and edit:
code .env
```

Key settings to update:
- `MONGODB_URL` — use `mongodb://localhost:27017` for local MongoDB
- `SECRET_KEY` — generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Step 5 — Run Phase 1 Detection Test

```powershell
# From the PROJECT ROOT (not inside backend/):
cd ..

# Run the test script (downloads sample video automatically if needed):
python scripts/test_detection.py

# Or with your webcam:
python scripts/test_detection.py --source 0

# Or with a specific video file:
python scripts/test_detection.py --source "C:\path\to\video.mp4"
```

**Expected result**: An OpenCV window opens showing the video with green bounding boxes around detected persons, an FPS counter in the top bar.

---

## Step 6 — Start FastAPI Backend (Phase 6+)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

API will be available at:
- http://localhost:8000/api/docs — Interactive Swagger UI
- http://localhost:8000/api/health — Health check

---

## Step 7 — Start React Frontend (Phase 7+)

Open a **second terminal** (keep backend running):

```powershell
cd frontend
npm install
npm run dev
```

Dashboard at: http://localhost:5173

---

## MongoDB Setup

### Option A — Local MongoDB (Recommended for Development)

1. Download MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Install with default settings
3. Start MongoDB service (should start automatically)
4. Verify: `mongosh` in a new terminal — you should see the MongoDB shell

### Option B — MongoDB Atlas (Cloud, Free Tier)

1. Create account at https://cloud.mongodb.com
2. Create a free M0 cluster
3. Create a database user
4. Get the connection string
5. Update `MONGODB_URL` in your `.env` file

---

## Common Problems and Fixes

### `Activate.ps1 cannot be loaded because running scripts is disabled`
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### `ModuleNotFoundError: No module named 'cv2'`
```powershell
pip install opencv-python
```

### `ModuleNotFoundError: No module named 'ultralytics'`
```powershell
pip install ultralytics
```

### OpenCV window does not appear / freezes
- Make sure you are NOT running inside a Docker container or remote SSH session
- Try adding `--no-display --save-output` flags to save output to a file instead

### YOLO model download fails
- Check your internet connection
- Try manually downloading from https://github.com/ultralytics/assets/releases
- Place `yolov8n.pt` in `model_weights/` folder

### `RuntimeError: Cannot open video source`
- Check the file path is correct
- For webcam, try `--source 0` or `--source 1`
- Ensure the video file is not corrupted
