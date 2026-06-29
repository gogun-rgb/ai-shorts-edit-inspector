from __future__ import annotations

import re
import shutil
from pathlib import Path
from uuid import uuid4

from app.core.errors import AnalysisNotFoundError, UserFacingError

MP4_CONTENT_TYPES = {"video/mp4", "application/mp4", "video/x-m4v"}
SUBTITLE_SUFFIXES = {".srt", ".vtt"}


def safe_uuid_name(suffix: str) -> str:
    normalized = Path(suffix).suffix.lower() or suffix.lower()
    if normalized and not normalized.startswith("."):
        normalized = f".{normalized}"
    if "/" in normalized or "\\" in normalized or ".." in normalized:
        normalized = ""
    return f"{uuid4()}{normalized}"


def validate_video_upload(filename: str, content_type: str | None, max_bytes: int, size: int | None) -> None:
    if Path(filename).suffix.lower() != ".mp4":
        raise UserFacingError("MP4 파일만 업로드할 수 있습니다.")
    if content_type and content_type not in MP4_CONTENT_TYPES:
        raise UserFacingError("업로드한 파일의 MIME 타입이 MP4로 확인되지 않습니다.")
    if size is not None and size > max_bytes:
        raise UserFacingError("업로드한 영상이 허용 용량을 초과했습니다.")


def validate_subtitle_upload(filename: str) -> None:
    if Path(filename).suffix.lower() not in SUBTITLE_SUFFIXES:
        raise UserFacingError("자막 파일은 SRT 또는 VTT만 지원합니다.")


def ensure_within_directory(base_dir: Path, target: Path) -> Path:
    base = base_dir.resolve()
    resolved = target.resolve()
    if base != resolved and base not in resolved.parents:
        raise UserFacingError("저장 경로가 허용된 폴더 밖으로 벗어났습니다.")
    return resolved


def safe_analysis_dir(storage_dir: Path, analysis_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", analysis_id):
        raise AnalysisNotFoundError("분석 ID가 올바르지 않습니다.", status_code=404)
    return ensure_within_directory(storage_dir, storage_dir / analysis_id)


def cleanup_analysis_dir(storage_dir: Path, analysis_id: str) -> bool:
    analysis_dir = safe_analysis_dir(storage_dir, analysis_id)
    if not analysis_dir.exists():
        return False
    shutil.rmtree(analysis_dir)
    return True
