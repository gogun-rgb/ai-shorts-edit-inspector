from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.models.findings import Finding
from app.models.transcript import TranscriptResult


class AnalysisStatus(StrEnum):
    QUEUED = "QUEUED"
    VALIDATING = "VALIDATING"
    EXTRACTING_METADATA = "EXTRACTING_METADATA"
    DETECTING_SILENCE = "DETECTING_SILENCE"
    TRANSCRIBING = "TRANSCRIBING"
    DETECTING_SCENES = "DETECTING_SCENES"
    BUILDING_REPORT = "BUILDING_REPORT"
    COMPLETED = "COMPLETED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"


class VideoMetadata(BaseModel):
    fileName: str
    fileSizeBytes: int
    duration: float
    width: int
    height: int
    aspectRatio: float
    fps: float | None = None
    videoCodec: str | None = None
    audioCodec: str | None = None
    hasAudio: bool
    averageBitrate: int | None = None


class Scene(BaseModel):
    index: int
    start: float
    end: float
    duration: float


class Summary(BaseModel):
    readinessScore: int
    grade: str
    totalFindings: int
    highCount: int
    mediumCount: int
    lowCount: int
    infoCount: int


class AnalysisResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    analysisId: str
    status: AnalysisStatus
    createdAt: datetime
    completedAt: datetime | None = None
    currentStep: AnalysisStatus | None = None
    metadata: VideoMetadata | None = None
    summary: Summary | None = None
    findings: list[Finding] = Field(default_factory=list)
    transcript: TranscriptResult | None = None
    scenes: list[Scene] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None


def utc_now() -> datetime:
    return datetime.now(UTC)
