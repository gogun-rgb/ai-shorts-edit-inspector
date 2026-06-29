from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FindingType(StrEnum):
    SILENCE = "SILENCE"
    START_SILENCE = "START_SILENCE"
    END_SILENCE = "END_SILENCE"
    LONG_SCENE = "LONG_SCENE"
    VERY_LONG_SCENE = "VERY_LONG_SCENE"
    SHORT_SCENE = "SHORT_SCENE"
    RAPID_CUTS = "RAPID_CUTS"
    SUBTITLE_GAP = "SUBTITLE_GAP"
    ASPECT_RATIO = "ASPECT_RATIO"
    VIDEO_DURATION = "VIDEO_DURATION"
    MISSING_AUDIO = "MISSING_AUDIO"
    TRANSCRIPTION_ERROR = "TRANSCRIPTION_ERROR"


class Severity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


SEVERITY_RANK: dict[Severity, int] = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
}


class Finding(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    type: FindingType
    severity: Severity
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    duration: float = Field(ge=0)
    title: str
    reason: str
    suggestion: str
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)

