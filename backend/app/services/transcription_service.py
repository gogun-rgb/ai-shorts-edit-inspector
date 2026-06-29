from __future__ import annotations

from pathlib import Path
from typing import Any

from app.models.transcript import TranscriptResult, TranscriptSegment, WordTimestamp

_MODEL_CACHE: dict[tuple[str, str, str], Any] = {}


def transcribe_video(
    video_path: Path,
    model_name: str,
    device: str,
    compute_type: str,
    language: str | None = None,
) -> TranscriptResult:
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:
        return TranscriptResult(error=f"faster-whisper를 사용할 수 없습니다: {exc}")

    cache_key = (model_name, device, compute_type)
    try:
        model = _MODEL_CACHE.get(cache_key)
        if model is None:
            model = WhisperModel(model_name, device=device, compute_type=compute_type)
            _MODEL_CACHE[cache_key] = model
        segments_iter, info = model.transcribe(
            str(video_path),
            language=language or None,
            vad_filter=True,
            word_timestamps=True,
        )
        segments: list[TranscriptSegment] = []
        for index, segment in enumerate(segments_iter):
            words = [
                WordTimestamp(start=float(word.start), end=float(word.end), word=word.word)
                for word in getattr(segment, "words", None) or []
                if word.start is not None and word.end is not None
            ]
            segments.append(
                TranscriptSegment(
                    id=index,
                    start=round(float(segment.start), 3),
                    end=round(float(segment.end), 3),
                    text=segment.text.strip(),
                    words=words,
                )
            )
        return TranscriptResult(
            language=getattr(info, "language", None),
            languageProbability=getattr(info, "language_probability", None),
            duration=getattr(info, "duration", None),
            segments=segments,
        )
    except Exception as exc:
        return TranscriptResult(error=f"Whisper transcript 생성에 실패했습니다: {exc}")

