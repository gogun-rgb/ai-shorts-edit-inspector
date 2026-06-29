from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from app.core.errors import UserFacingError
from app.models.analysis import VideoMetadata
from app.services.ffmpeg_service import ffprobe_json


def rational_to_float(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    try:
        return round(float(Fraction(value)), 3)
    except (ValueError, ZeroDivisionError):
        try:
            return round(float(value), 3)
        except ValueError:
            return None


def extract_metadata(video_path: Path, original_name: str) -> VideoMetadata:
    data = ffprobe_json(video_path)
    streams = data.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio_stream = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    if not video_stream:
        raise UserFacingError("업로드한 파일에서 비디오 스트림을 찾을 수 없습니다.")

    duration_text = (
        video_stream.get("duration")
        or data.get("format", {}).get("duration")
        or "0"
    )
    try:
        duration = round(float(duration_text), 3)
    except ValueError as exc:
        raise UserFacingError("영상 길이를 확인할 수 없습니다.") from exc
    if duration <= 0:
        raise UserFacingError("영상 길이가 올바르지 않습니다.")

    width = int(video_stream.get("width") or 0)
    height = int(video_stream.get("height") or 0)
    if width <= 0 or height <= 0:
        raise UserFacingError("영상 해상도를 확인할 수 없습니다.")

    bitrate_text = data.get("format", {}).get("bit_rate")
    average_bitrate = None
    if bitrate_text:
        try:
            average_bitrate = int(float(bitrate_text))
        except ValueError:
            average_bitrate = None

    return VideoMetadata(
        fileName=original_name,
        fileSizeBytes=video_path.stat().st_size,
        duration=duration,
        width=width,
        height=height,
        aspectRatio=round(width / height, 4),
        fps=rational_to_float(video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate")),
        videoCodec=video_stream.get("codec_name"),
        audioCodec=audio_stream.get("codec_name") if audio_stream else None,
        hasAudio=audio_stream is not None,
        averageBitrate=average_bitrate,
    )

