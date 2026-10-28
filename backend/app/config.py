"""
config.py - Application Configuration
=====================================
Loads settings from the .env file using Pydantic Settings.
All configurable values are defined here with sensible defaults.

Usage:
    from app.config import settings
    print(settings.MONGODB_URL)
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


# Base directory of the backend/ folder
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Reads environment variables from backend/.env
    Falls back to defaults if a variable is not set.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── MongoDB ──────────────────────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "construction_safety"

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # ── Default Admin ────────────────────────────────────────────────────────
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "Admin@1234"
    ADMIN_EMAIL: str = "admin@example.com"

    # ── Detection ────────────────────────────────────────────────────────────
    DETECTION_CONFIDENCE: float = 0.50
    PPE_CERTAIN_THRESHOLD: float = 0.65

    # ── Violation Rules ──────────────────────────────────────────────────────
    VIOLATION_PERSISTENCE_SECONDS: float = 3.0
    ALERT_COOLDOWN_SECONDS: float = 30.0
    PERSISTENCE_FRAME_BUFFER: int = 10

    # ── Video Processing ─────────────────────────────────────────────────────
    MODEL_PATH: str = "../model_weights/yolov8n.pt"
    MAX_FRAME_WIDTH: int = 1280
    FRAME_SKIP: int = 1
    MAX_CONCURRENT_STREAMS: int = 2

    # ── Evidence ─────────────────────────────────────────────────────────────
    EVIDENCE_DIR: str = "../evidence"
    SAVE_EVIDENCE_FRAMES: bool = True
    MAX_EVIDENCE_IMAGES: int = 1000

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # ── Computed Properties ──────────────────────────────────────────────────
    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def model_path_resolved(self) -> Path:
        """Resolve model path relative to backend root."""
        p = Path(self.MODEL_PATH)
        if p.is_absolute():
            return p
        return (BASE_DIR / self.MODEL_PATH).resolve()

    @property
    def evidence_dir_resolved(self) -> Path:
        """Resolve evidence directory path."""
        p = Path(self.EVIDENCE_DIR)
        if p.is_absolute():
            return p
        return (BASE_DIR / self.EVIDENCE_DIR).resolve()

    @field_validator("DETECTION_CONFIDENCE", "PPE_CERTAIN_THRESHOLD")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence thresholds must be between 0.0 and 1.0")
        return v

    @field_validator("FRAME_SKIP")
    @classmethod
    def validate_frame_skip(cls, v: int) -> int:
        if v < 1:
            raise ValueError("FRAME_SKIP must be at least 1")
        return v


# Singleton instance used throughout the application
settings = Settings()
