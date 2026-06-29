from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from app.core.errors import ToolUnavailableError, UserFacingError


def binary_available(name: str) -> bool:
    return shutil.which(name) is not None


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise ToolUnavailableError(
            f"{name} 실행 파일을 찾을 수 없습니다. FFmpeg 설치와 PATH 설정을 확인하세요.",
            status_code=503,
        )
    return path


def run_command(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise UserFacingError("영상 분석 명령이 제한 시간을 초과했습니다.") from exc
    except OSError as exc:
        raise UserFacingError("로컬 영상 분석 도구를 실행하지 못했습니다.") from exc


def ffprobe_json(video_path: Path) -> dict:
    ffprobe = require_binary("ffprobe")
    result = run_command(
        [
            ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ],
        timeout=60,
    )
    if result.returncode != 0:
        raise UserFacingError("ffprobe가 실제 영상 파일로 확인하지 못했습니다.")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise UserFacingError("ffprobe 결과를 해석하지 못했습니다.") from exc


def run_silencedetect(video_path: Path, threshold_db: float, min_duration: float) -> str:
    ffmpeg = require_binary("ffmpeg")
    result = run_command(
        [
            ffmpeg,
            "-hide_banner",
            "-nostdin",
            "-i",
            str(video_path),
            "-af",
            f"silencedetect=n={threshold_db}dB:d={min_duration}",
            "-f",
            "null",
            "-",
        ],
        timeout=180,
    )
    if result.returncode != 0:
        raise UserFacingError("FFmpeg 무음 분석에 실패했습니다.")
    return result.stderr

