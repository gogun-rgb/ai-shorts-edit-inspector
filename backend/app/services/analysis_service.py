from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import Settings, get_settings
from app.core.errors import AnalysisNotFoundError, UserFacingError
from app.models.analysis import AnalysisResult, AnalysisStatus, utc_now
from app.models.transcript import TranscriptResult
from app.services.metadata_service import extract_metadata
from app.services.report_service import (
    RULE_BASED_DISCLAIMER,
    build_scene_findings,
    build_silence_findings,
    build_spec_findings,
    build_subtitle_gap_findings,
    build_summary,
    findings_to_csv,
    merge_similar_findings,
)
from app.services.scene_detector import detect_scenes
from app.services.silence_detector import detect_silence
from app.services.subtitle_service import parse_subtitle_file, transcript_segments_without_subtitle
from app.services.transcription_service import transcribe_video
from app.utils.files import (
    cleanup_analysis_dir,
    ensure_within_directory,
    safe_analysis_dir,
    validate_subtitle_upload,
    validate_video_upload,
)

_ANALYSES: dict[str, AnalysisResult] = {}


def storage_dir(settings: Settings | None = None) -> Path:
    active_settings = settings or get_settings()
    active_settings.storage_dir.mkdir(parents=True, exist_ok=True)
    return active_settings.storage_dir


def result_path(analysis_id: str, settings: Settings | None = None) -> Path:
    base_dir = storage_dir(settings)
    return ensure_within_directory(base_dir, safe_analysis_dir(base_dir, analysis_id) / "result.json")


def _save_result(result: AnalysisResult, settings: Settings | None = None) -> None:
    path = result_path(result.analysisId, settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def _load_result(analysis_id: str, settings: Settings | None = None) -> AnalysisResult:
    path = result_path(analysis_id, settings)
    if not path.exists():
        raise AnalysisNotFoundError("분석 결과를 찾을 수 없습니다.", status_code=404)
    return AnalysisResult.model_validate_json(path.read_text(encoding="utf-8"))


def get_analysis(analysis_id: str, settings: Settings | None = None) -> AnalysisResult:
    if analysis_id in _ANALYSES:
        return _ANALYSES[analysis_id]
    return _load_result(analysis_id, settings)


async def create_analysis(
    video: UploadFile,
    subtitle: UploadFile | None = None,
    settings: Settings | None = None,
) -> tuple[AnalysisResult, Path, Path | None]:
    active_settings = settings or get_settings()
    validate_video_upload(
        video.filename or "",
        video.content_type,
        active_settings.max_upload_bytes,
        getattr(video, "size", None),
    )
    if subtitle is not None:
        validate_subtitle_upload(subtitle.filename or "")

    analysis_id = str(uuid4())
    created = AnalysisResult(
        analysisId=analysis_id,
        status=AnalysisStatus.QUEUED,
        currentStep=AnalysisStatus.QUEUED,
        createdAt=utc_now(),
        warnings=[RULE_BASED_DISCLAIMER],
    )
    _ANALYSES[analysis_id] = created

    analysis_dir = safe_analysis_dir(storage_dir(active_settings), analysis_id)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    video_path = ensure_within_directory(analysis_dir, analysis_dir / "source.mp4")
    subtitle_path = None

    await _copy_upload(video, video_path, active_settings.max_upload_bytes)
    if subtitle is not None:
        suffix = Path(subtitle.filename or "subtitle.srt").suffix.lower()
        subtitle_path = ensure_within_directory(analysis_dir, analysis_dir / f"subtitle{suffix}")
        await _copy_upload(subtitle, subtitle_path, 5 * 1024 * 1024)

    _save_result(created, active_settings)
    return created, video_path, subtitle_path


async def _copy_upload(upload: UploadFile, destination: Path, max_bytes: int) -> None:
    total = 0
    try:
        with destination.open("wb") as handle:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise UserFacingError("업로드한 파일이 허용 용량을 초과했습니다.")
                handle.write(chunk)
    except Exception:
        if destination.exists():
            destination.unlink()
        raise
    finally:
        await upload.close()


def _update_status(result: AnalysisResult, status: AnalysisStatus, settings: Settings) -> None:
    result.status = status
    result.currentStep = status
    _ANALYSES[result.analysisId] = result
    _save_result(result, settings)


def run_analysis(
    analysis_id: str,
    video_path: Path,
    subtitle_path: Path | None = None,
    language: str | None = None,
    silence_threshold_db: float | None = None,
    min_silence_duration: float | None = None,
    long_scene_seconds: float | None = None,
    settings: Settings | None = None,
) -> None:
    active_settings = settings or get_settings()
    result = get_analysis(analysis_id, active_settings)
    warnings = list(result.warnings)
    try:
        _update_status(result, AnalysisStatus.VALIDATING, active_settings)
        _update_status(result, AnalysisStatus.EXTRACTING_METADATA, active_settings)
        metadata = extract_metadata(video_path, "source.mp4")
        result.metadata = metadata
        if metadata.duration > active_settings.max_video_duration_seconds:
            raise UserFacingError(
                f"영상 길이가 {active_settings.max_video_duration_seconds}초 제한을 초과했습니다.",
            )

        threshold_db = (
            silence_threshold_db if silence_threshold_db is not None else active_settings.silence_threshold_db
        )
        min_duration = (
            min_silence_duration if min_silence_duration is not None else active_settings.min_silence_duration
        )
        long_scene = long_scene_seconds if long_scene_seconds is not None else active_settings.long_scene_seconds

        findings = build_spec_findings(metadata)
        transcript = TranscriptResult(duration=metadata.duration)

        if metadata.hasAudio:
            _update_status(result, AnalysisStatus.DETECTING_SILENCE, active_settings)
            try:
                intervals = detect_silence(video_path, threshold_db, min_duration, metadata.duration)
                findings.extend(build_silence_findings(intervals, threshold_db, metadata.duration))
            except UserFacingError as exc:
                warnings.append(exc.message)

            _update_status(result, AnalysisStatus.TRANSCRIBING, active_settings)
            transcript = transcribe_video(
                video_path,
                active_settings.whisper_model,
                active_settings.whisper_device,
                active_settings.whisper_compute_type,
                language,
            )
            if transcript.error:
                warnings.append(transcript.error)
        else:
            warnings.append("오디오 스트림이 없어 무음 분석과 transcript 생성을 건너뛰었습니다.")

        _update_status(result, AnalysisStatus.DETECTING_SCENES, active_settings)
        scenes, scene_warning = detect_scenes(video_path, metadata.duration, active_settings.scene_threshold)
        if scene_warning:
            warnings.append(scene_warning)
        findings.extend(
            build_scene_findings(
                scenes,
                long_scene,
                active_settings.very_long_scene_seconds,
                active_settings.short_scene_seconds,
                active_settings.rapid_cut_window_seconds,
                active_settings.rapid_cut_min_count,
                metadata.duration,
            )
        )

        if subtitle_path is not None and transcript.segments:
            cues = parse_subtitle_file(subtitle_path)
            missing = transcript_segments_without_subtitle(
                transcript.segments,
                cues,
                active_settings.subtitle_tolerance_seconds,
            )
            findings.extend(build_subtitle_gap_findings(missing, metadata.duration))
        elif subtitle_path is None:
            warnings.append("자막 파일이 없어 실제 자막 누락 여부는 비교할 수 없습니다.")

        _update_status(result, AnalysisStatus.BUILDING_REPORT, active_settings)
        result.findings = merge_similar_findings(findings, metadata.duration)
        result.summary = build_summary(result.findings)
        result.transcript = transcript
        result.scenes = scenes
        result.warnings = warnings
        result.completedAt = utc_now()
        partial_markers = ("실패", "오디오 스트림이 없어", "초기화하지 못해", "장면 분석에 실패")
        result.status = (
            AnalysisStatus.PARTIAL_SUCCESS
            if any(any(marker in warning for marker in partial_markers) for warning in warnings)
            else AnalysisStatus.COMPLETED
        )
        result.currentStep = result.status
        _ANALYSES[analysis_id] = result
        _save_result(result, active_settings)
    except UserFacingError as exc:
        result.status = AnalysisStatus.FAILED
        result.currentStep = AnalysisStatus.FAILED
        result.error = exc.message
        result.completedAt = utc_now()
        _ANALYSES[analysis_id] = result
        _save_result(result, active_settings)
    except Exception as exc:  # pragma: no cover - defensive boundary.
        result.status = AnalysisStatus.FAILED
        result.currentStep = AnalysisStatus.FAILED
        result.error = f"분석 중 예상하지 못한 오류가 발생했습니다: {exc.__class__.__name__}"
        result.completedAt = utc_now()
        _ANALYSES[analysis_id] = result
        _save_result(result, active_settings)


def export_json(analysis_id: str, settings: Settings | None = None) -> str:
    result = get_analysis(analysis_id, settings)
    return result.model_dump_json(indent=2)


def export_csv(analysis_id: str, settings: Settings | None = None) -> str:
    result = get_analysis(analysis_id, settings)
    return findings_to_csv(result.findings)


def video_file_path(analysis_id: str, settings: Settings | None = None) -> Path:
    base_dir = storage_dir(settings)
    path = ensure_within_directory(base_dir, safe_analysis_dir(base_dir, analysis_id) / "source.mp4")
    if not path.exists():
        raise AnalysisNotFoundError("영상 파일을 찾을 수 없습니다.", status_code=404)
    return path


def delete_analysis(analysis_id: str, settings: Settings | None = None) -> bool:
    _ANALYSES.pop(analysis_id, None)
    return cleanup_analysis_dir(storage_dir(settings), analysis_id)


def cleanup_old_analyses(settings: Settings | None = None) -> int:
    active_settings = settings or get_settings()
    base_dir = storage_dir(active_settings)
    cutoff_seconds = active_settings.analysis_retention_hours * 3600
    removed = 0
    now = utc_now().timestamp()
    for child in base_dir.iterdir():
        if not child.is_dir():
            continue
        try:
            age = now - child.stat().st_mtime
        except OSError:
            continue
        if age > cutoff_seconds:
            shutil.rmtree(child, ignore_errors=True)
            _ANALYSES.pop(child.name, None)
            removed += 1
    return removed
