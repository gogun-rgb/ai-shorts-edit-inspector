from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.services.ffmpeg_service import binary_available

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "version": settings.app_version,
        "ffmpegAvailable": binary_available("ffmpeg"),
        "ffprobeAvailable": binary_available("ffprobe"),
        "whisper": {
            "model": settings.whisper_model,
            "device": settings.whisper_device,
            "computeType": settings.whisper_compute_type,
        },
    }

