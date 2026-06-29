from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.services.ffmpeg_service import run_silencedetect
from app.utils.timestamps import clamp_time


@dataclass(frozen=True)
class SilenceInterval:
    start: float
    end: float
    duration: float


_START_RE = re.compile(r"silence_start:\s*(-?\d+(?:\.\d+)?)")
_END_RE = re.compile(
    r"silence_end:\s*(-?\d+(?:\.\d+)?)\s*\|\s*silence_duration:\s*(-?\d+(?:\.\d+)?)"
)


def parse_silence_log(log: str, video_duration: float | None = None) -> list[SilenceInterval]:
    intervals: list[SilenceInterval] = []
    current_start: float | None = None

    for line in log.splitlines():
        start_match = _START_RE.search(line)
        if start_match:
            try:
                parsed = float(start_match.group(1))
            except ValueError:
                continue
            if parsed >= 0:
                current_start = parsed
            continue

        end_match = _END_RE.search(line)
        if not end_match:
            continue
        try:
            end = float(end_match.group(1))
            duration = float(end_match.group(2))
        except ValueError:
            continue
        if end < 0 or duration < 0:
            continue
        start = current_start if current_start is not None else end - duration
        start = clamp_time(start, video_duration)
        end = clamp_time(end, video_duration)
        if end > start:
            intervals.append(SilenceInterval(start=start, end=end, duration=round(end - start, 3)))
        current_start = None

    if current_start is not None and video_duration is not None and video_duration > current_start:
        start = clamp_time(current_start, video_duration)
        end = clamp_time(video_duration, video_duration)
        intervals.append(SilenceInterval(start=start, end=end, duration=round(end - start, 3)))

    return intervals


def detect_silence(
    video_path: Path,
    threshold_db: float,
    min_duration: float,
    video_duration: float,
) -> list[SilenceInterval]:
    log = run_silencedetect(video_path, threshold_db, min_duration)
    return parse_silence_log(log, video_duration=video_duration)
