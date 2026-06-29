from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_env: str
    app_version: str
    frontend_origin: str
    storage_dir: Path
    max_upload_mb: int
    max_video_duration_seconds: int
    whisper_model: str
    whisper_device: str
    whisper_compute_type: str
    silence_threshold_db: float
    min_silence_duration: float
    long_scene_seconds: float
    very_long_scene_seconds: float
    short_scene_seconds: float
    rapid_cut_window_seconds: float
    rapid_cut_min_count: int
    scene_threshold: float
    subtitle_tolerance_seconds: float
    analysis_retention_hours: int

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


def get_settings() -> Settings:
    backend_dir = Path(__file__).resolve().parents[2]
    default_storage = backend_dir.parent.parent / "storage" / "analyses"
    storage_dir = Path(os.getenv("STORAGE_DIR", str(default_storage))).expanduser()
    if not storage_dir.is_absolute():
        storage_dir = (backend_dir / storage_dir).resolve()

    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        app_version=os.getenv("APP_VERSION", "0.1.1"),
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
        storage_dir=storage_dir.resolve(),
        max_upload_mb=_env_int("MAX_UPLOAD_MB", 500),
        max_video_duration_seconds=_env_int("MAX_VIDEO_DURATION_SECONDS", 180),
        whisper_model=os.getenv("WHISPER_MODEL", "base"),
        whisper_device=os.getenv("WHISPER_DEVICE", "cpu"),
        whisper_compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
        silence_threshold_db=_env_float("SILENCE_THRESHOLD_DB", -35.0),
        min_silence_duration=_env_float("MIN_SILENCE_DURATION", 0.8),
        long_scene_seconds=_env_float("LONG_SCENE_SECONDS", 6.0),
        very_long_scene_seconds=_env_float("VERY_LONG_SCENE_SECONDS", 10.0),
        short_scene_seconds=_env_float("SHORT_SCENE_SECONDS", 0.45),
        rapid_cut_window_seconds=_env_float("RAPID_CUT_WINDOW_SECONDS", 3.0),
        rapid_cut_min_count=_env_int("RAPID_CUT_MIN_COUNT", 4),
        scene_threshold=_env_float("SCENE_THRESHOLD", 27.0),
        subtitle_tolerance_seconds=_env_float("SUBTITLE_TOLERANCE_SECONDS", 0.3),
        analysis_retention_hours=_env_int("ANALYSIS_RETENTION_HOURS", 24),
    )
