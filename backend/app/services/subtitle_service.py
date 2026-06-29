from __future__ import annotations

import re
from pathlib import Path

from app.core.errors import UserFacingError
from app.models.transcript import SubtitleCue, TranscriptSegment

_TIME_RE = re.compile(
    r"(?P<h>\d{1,2}):(?P<m>\d{2}):(?P<s>\d{2})(?P<ms>[\.,]\d{1,3})?"
)


def _parse_time(value: str) -> float:
    match = _TIME_RE.search(value.strip())
    if not match:
        raise ValueError(value)
    milliseconds = match.group("ms") or ".0"
    milliseconds = milliseconds.replace(",", ".")
    return (
        int(match.group("h")) * 3600
        + int(match.group("m")) * 60
        + int(match.group("s"))
        + float(milliseconds)
    )


def parse_subtitle_file(path: Path) -> list[SubtitleCue]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"^WEBVTT.*?\n\n", "", text, flags=re.DOTALL)
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    cues: list[SubtitleCue] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        timing_line_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_line_index is None:
            continue
        left, right = lines[timing_line_index].split("-->", maxsplit=1)
        try:
            start = _parse_time(left)
            end = _parse_time(right)
        except ValueError as exc:
            raise UserFacingError("자막 타임스탬프를 해석하지 못했습니다.") from exc
        if end <= start:
            continue
        cue_text = " ".join(lines[timing_line_index + 1 :]).strip()
        cues.append(SubtitleCue(index=len(cues), start=round(start, 3), end=round(end, 3), text=cue_text))
    return cues


def overlaps_with_tolerance(
    start: float,
    end: float,
    cue: SubtitleCue,
    tolerance: float,
) -> bool:
    return max(start, cue.start - tolerance) < min(end, cue.end + tolerance)


def transcript_segments_without_subtitle(
    transcript_segments: list[TranscriptSegment],
    subtitle_cues: list[SubtitleCue],
    tolerance: float,
    min_duration: float = 0.8,
) -> list[TranscriptSegment]:
    missing: list[TranscriptSegment] = []
    for segment in transcript_segments:
        duration = segment.end - segment.start
        if duration < min_duration:
            continue
        if not any(overlaps_with_tolerance(segment.start, segment.end, cue, tolerance) for cue in subtitle_cues):
            missing.append(segment)
    return missing

