from __future__ import annotations

from pydantic import BaseModel, Field


class WordTimestamp(BaseModel):
    start: float
    end: float
    word: str


class TranscriptSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    words: list[WordTimestamp] = Field(default_factory=list)


class TranscriptResult(BaseModel):
    language: str | None = None
    languageProbability: float | None = None
    duration: float | None = None
    segments: list[TranscriptSegment] = Field(default_factory=list)
    error: str | None = None


class SubtitleCue(BaseModel):
    index: int
    start: float
    end: float
    text: str

