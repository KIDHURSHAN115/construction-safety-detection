"""
main.py - FastAPI Application Entry Point
==========================================
STATUS: Skeleton — expanded in Phase 6.

Currently provides:
  - GET /api/health     : Health check endpoint (works now)
  - GET /               : API info

Phase 6 will add:
  - Authentication endpoints
  - Video upload and monitoring endpoints
  - WebSocket for real-time updates
  - Violation management endpoints
  - Dashboard summary endpoint
  - Settings endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from app.config import settings

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Construction Site Safety Detection API",
    description=(
        "AI-powered construction site safety violation detection system. "
        "Detects PPE violations, tracks workers, and generates real-time alerts."
    ),
    version="0.1.0-phase1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup / Shutdown events ─────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("Construction Safety Detection API starting up...")
    logger.info(f"    Phase: 1 (Detection Prototype)")
    logger.info(f"    Docs:  http://localhost:8000/api/docs")
    # Phase 6: Initialize MongoDB connection
    # Phase 6: Create default admin user
    # Phase 6: Load detection model


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API shutting down...")
    # Phase 6: Close MongoDB connection
    # Phase 6: Stop active video streams


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
async def health_check():
    """
    Returns the API health status.
    This endpoint does NOT require authentication.
    """
    return {
        "status": "healthy",
        "version": "0.1.0-phase1",
        "phase": 1,
        "message": "API is running. Detection engine and database will be connected in Phase 6.",
        "features": {
            "detection": "standalone script only (Phase 6 for API)",
            "tracking": "Phase 3",
            "violations": "Phase 4",
            "dashboard": "Phase 7",
            "websocket": "Phase 8",
        }
    }


@app.get("/", tags=["System"])
async def root():
    """API root — redirects to documentation."""
    return {
        "message": "Construction Site Safety Detection API",
        "docs": "/api/docs",
        "health": "/api/health",
        "phase": 1,
    }


# ── Placeholder routes (to be implemented in Phase 6) ─────────────────────────
@app.get("/api/dashboard/summary", tags=["Dashboard"])
async def dashboard_summary():
    """
    Returns dashboard summary statistics.
    Phase 1: Returns placeholder data.
    Phase 6: Returns live data from MongoDB.
    """
    return {
        "note": "Phase 1 placeholder — real data available after Phase 6",
        "total_workers_detected": 0,
        "total_violations": 0,
        "active_streams": 0,
        "violations_today": 0,
        "violations_by_type": {},
        "recent_alerts": [],
    }
