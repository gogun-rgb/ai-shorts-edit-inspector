from __future__ import annotations

import csv
import io
from uuid import uuid4

from app.models.analysis import Scene, Summary, VideoMetadata
from app.models.findings import SEVERITY_RANK, Finding, FindingType, Severity
from app.models.transcript import TranscriptSegment
from app.services.silence_detector import SilenceInterval
from app.utils.timestamps import clamp_time, format_timestamp

RULE_BASED_DISCLAIMER = (
    "이 분석 결과는 자동 편집 보조를 위한 규칙 기반 진단이며, 최종 편집 판단은 사용자가 내려야 합니다."
)


def _finding(
    finding_type: FindingType,
    severity: Severity,
    start: float,
    end: float,
    title: str,
    reason: str,
    suggestion: str,
    source: str,
    metadata: dict | None = None,
    video_duration: float | None = None,
) -> Finding:
    safe_start = clamp_time(start, video_duration)
    safe_end = clamp_time(max(end, safe_start), video_duration)
    return Finding(
        id=str(uuid4()),
        type=finding_type,
        severity=severity,
        start=safe_start,
        end=safe_end,
        duration=round(max(0.0, safe_end - safe_start), 3),
        title=title,
        reason=reason,
        suggestion=suggestion,
        source=source,
        metadata=metadata or {},
    )


def severity_for_silence(duration: float) -> Severity:
    if duration >= 2.5:
        return Severity.HIGH
    if duration >= 1.5:
        return Severity.MEDIUM
    return Severity.LOW


def build_silence_findings(
    intervals: list[SilenceInterval],
    threshold_db: float,
    video_duration: float,
) -> list[Finding]:
    findings: list[Finding] = []
    for interval in intervals:
        finding_type = FindingType.SILENCE
        title = "긴 무음 구간"
        suggestion = "무음 제거, B-roll 삽입 또는 문장 간격 단축을 검토하세요."
        if interval.start <= 2 and interval.duration >= 0.8:
            finding_type = FindingType.START_SILENCE
            title = "시작 부분 무음"
            suggestion = "첫 문장이나 시각적 훅을 앞당기는 것을 검토하세요."
        elif video_duration - interval.end <= 2 and interval.duration >= 0.8:
            finding_type = FindingType.END_SILENCE
            title = "끝부분 무음"
            suggestion = "영상 끝의 불필요한 정적 구간을 짧게 정리하는 것을 검토하세요."
        findings.append(
            _finding(
                finding_type,
                severity_for_silence(interval.duration),
                interval.start,
                interval.end,
                title,
                f"{interval.duration:.1f}초 동안 음량이 {threshold_db:g}dB 이하였습니다.",
                suggestion,
                "FFMPEG_SILENCE_DETECTOR",
                {"thresholdDb": threshold_db},
                video_duration,
            )
        )
    return findings


def build_scene_findings(
    scenes: list[Scene],
    long_scene_seconds: float,
    very_long_scene_seconds: float,
    short_scene_seconds: float,
    rapid_cut_window_seconds: float,
    rapid_cut_min_count: int,
    video_duration: float,
) -> list[Finding]:
    findings: list[Finding] = []
    for scene in scenes:
        if scene.duration >= very_long_scene_seconds:
            findings.append(
                _finding(
                    FindingType.VERY_LONG_SCENE,
                    Severity.HIGH,
                    scene.start,
                    scene.end,
                    "매우 긴 단일 장면",
                    f"화면 전환 없이 {scene.duration:.1f}초 지속되었습니다.",
                    "B-roll, 구도 변경, 핵심 단어 강조 또는 의도된 장면인지 확인하세요.",
                    "PYSCENEDETECT_RULE_ENGINE",
                    {"sceneIndex": scene.index},
                    video_duration,
                )
            )
        elif scene.duration >= long_scene_seconds:
            findings.append(
                _finding(
                    FindingType.LONG_SCENE,
                    Severity.MEDIUM,
                    scene.start,
                    scene.end,
                    "긴 단일 장면",
                    f"화면 전환 없이 {scene.duration:.1f}초 지속되었습니다.",
                    "화면 확대 또는 축소, 자막 강조 방식 변경, 보조 화면 추가를 검토하세요.",
                    "PYSCENEDETECT_RULE_ENGINE",
                    {"sceneIndex": scene.index},
                    video_duration,
                )
            )

    short_scenes = [scene for scene in scenes if scene.duration < short_scene_seconds]
    for scene in short_scenes:
        findings.append(
            _finding(
                FindingType.SHORT_SCENE,
                Severity.LOW,
                scene.start,
                scene.end,
                "짧은 컷 후보",
                f"{scene.duration:.2f}초 장면이 감지되었습니다.",
                "의도하지 않은 1~2프레임 잔여 컷인지 확인하세요.",
                "PYSCENEDETECT_RULE_ENGINE",
                {"sceneIndex": scene.index},
                video_duration,
            )
        )

    for index in range(len(short_scenes)):
        window = [
            scene
            for scene in short_scenes[index:]
            if scene.start - short_scenes[index].start <= rapid_cut_window_seconds
        ]
        if len(window) >= rapid_cut_min_count:
            findings.append(
                _finding(
                    FindingType.RAPID_CUTS,
                    Severity.HIGH,
                    window[0].start,
                    window[-1].end,
                    "빠른 컷 확인 필요",
                    f"{rapid_cut_window_seconds:g}초 안에 짧은 컷 {len(window)}개가 이어졌습니다.",
                    "전환 효과 중복, 잔여 프레임, 시청자가 내용을 인식할 시간 확보 여부를 확인하세요.",
                    "PYSCENEDETECT_RULE_ENGINE",
                    {"shortSceneCount": len(window)},
                    video_duration,
                )
            )
            break
    return findings


def build_spec_findings(metadata: VideoMetadata) -> list[Finding]:
    findings: list[Finding] = []
    target_ratio = 9 / 16
    ratio_delta = abs(metadata.aspectRatio - target_ratio)
    if metadata.width >= metadata.height or ratio_delta > 0.12:
        findings.append(
            _finding(
                FindingType.ASPECT_RATIO,
                Severity.MEDIUM,
                0,
                min(metadata.duration, 1),
                "쇼츠 화면 비율 확인",
                f"현재 화면 비율은 {metadata.width}:{metadata.height}입니다.",
                "세로 9:16에 가까운 구도인지 확인하세요.",
                "VIDEO_METADATA_RULE_ENGINE",
                {"aspectRatio": metadata.aspectRatio},
                metadata.duration,
            )
        )
    if metadata.duration < 15:
        findings.append(
            _finding(
                FindingType.VIDEO_DURATION,
                Severity.INFO,
                0,
                metadata.duration,
                "짧은 영상 길이",
                f"영상 길이가 {metadata.duration:.1f}초입니다.",
                "정보 전달 시간이 충분한지 확인하세요. 이는 프로젝트 내부 참고 기준입니다.",
                "VIDEO_METADATA_RULE_ENGINE",
                video_duration=metadata.duration,
            )
        )
    elif metadata.duration > 60:
        findings.append(
            _finding(
                FindingType.VIDEO_DURATION,
                Severity.LOW,
                0,
                metadata.duration,
                "긴 쇼츠 길이",
                f"영상 길이가 {metadata.duration:.1f}초입니다.",
                "핵심 메시지가 뒤로 밀리지 않는지 확인하세요. 이는 프로젝트 내부 참고 기준입니다.",
                "VIDEO_METADATA_RULE_ENGINE",
                video_duration=metadata.duration,
            )
        )
    if not metadata.hasAudio:
        findings.append(
            _finding(
                FindingType.MISSING_AUDIO,
                Severity.INFO,
                0,
                min(metadata.duration, 1),
                "오디오 스트림 없음",
                "영상에서 오디오 스트림을 찾지 못했습니다.",
                "무음 분석과 transcript는 사용할 수 없지만 장면과 규격 분석은 계속됩니다.",
                "VIDEO_METADATA_RULE_ENGINE",
                video_duration=metadata.duration,
            )
        )
    return findings


def build_subtitle_gap_findings(
    missing_segments: list[TranscriptSegment],
    video_duration: float,
) -> list[Finding]:
    findings: list[Finding] = []
    for segment in missing_segments:
        duration = segment.end - segment.start
        findings.append(
            _finding(
                FindingType.SUBTITLE_GAP,
                Severity.HIGH if duration >= 1.5 else Severity.MEDIUM,
                segment.start,
                segment.end,
                "자막 공백 후보",
                f"{duration:.1f}초 음성 구간과 겹치는 자막 구간이 없습니다.",
                "해당 음성 구간에 자막이 필요한지 확인하세요.",
                "SUBTITLE_TRANSCRIPT_COMPARATOR",
                {"textPreview": segment.text[:80]},
                video_duration,
            )
        )
    return findings


def overlap_ratio(left: Finding, right: Finding) -> float:
    intersection = max(0.0, min(left.end, right.end) - max(left.start, right.start))
    shorter = max(0.001, min(left.duration, right.duration))
    return intersection / shorter


def merge_similar_findings(findings: list[Finding], video_duration: float | None = None) -> list[Finding]:
    ordered = sorted(findings, key=lambda item: (item.start, item.end, item.type))
    merged: list[Finding] = []
    for finding in ordered:
        match = next(
            (
                existing
                for existing in merged
                if existing.type == finding.type and overlap_ratio(existing, finding) >= 0.8
            ),
            None,
        )
        if match is None:
            finding.start = clamp_time(finding.start, video_duration)
            finding.end = clamp_time(finding.end, video_duration)
            finding.duration = round(max(0.0, finding.end - finding.start), 3)
            merged.append(finding)
            continue
        match.start = min(match.start, finding.start)
        match.end = max(match.end, finding.end)
        match.end = clamp_time(match.end, video_duration)
        match.duration = round(max(0.0, match.end - match.start), 3)
        if SEVERITY_RANK[Severity(finding.severity)] > SEVERITY_RANK[Severity(match.severity)]:
            match.severity = finding.severity
        match.metadata = {**match.metadata, **finding.metadata}
    return sorted(merged, key=lambda item: item.start)


def calculate_readiness_score(findings: list[Finding]) -> int:
    score = 100
    for finding in findings:
        severity = Severity(finding.severity)
        if severity == Severity.HIGH:
            score -= 12
        elif severity == Severity.MEDIUM:
            score -= 6
        elif severity == Severity.LOW:
            score -= 2

        finding_type = FindingType(finding.type)
        if finding_type == FindingType.START_SILENCE:
            score -= 5
        elif finding_type == FindingType.END_SILENCE:
            score -= 3
        elif finding_type == FindingType.VERY_LONG_SCENE:
            score -= 5
        elif finding_type == FindingType.RAPID_CUTS:
            score -= 5
        elif finding_type == FindingType.SUBTITLE_GAP:
            score -= 8 if finding.duration >= 1.5 else 3
        elif finding_type == FindingType.ASPECT_RATIO:
            score -= 8
    return min(100, max(0, score))


def grade_for_score(score: int) -> str:
    if score >= 90:
        return "Ready"
    if score >= 75:
        return "Minor fixes"
    if score >= 50:
        return "Needs review"
    return "Major review"


def build_summary(findings: list[Finding]) -> Summary:
    score = calculate_readiness_score(findings)
    return Summary(
        readinessScore=score,
        grade=grade_for_score(score),
        totalFindings=len(findings),
        highCount=sum(1 for finding in findings if finding.severity == Severity.HIGH),
        mediumCount=sum(1 for finding in findings if finding.severity == Severity.MEDIUM),
        lowCount=sum(1 for finding in findings if finding.severity == Severity.LOW),
        infoCount=sum(1 for finding in findings if finding.severity == Severity.INFO),
    )


def findings_to_csv(findings: list[Finding]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["start", "end", "type", "severity", "title", "reason", "suggestion"])
    for finding in findings:
        writer.writerow(
            [
                format_timestamp(finding.start),
                format_timestamp(finding.end),
                finding.type,
                finding.severity,
                finding.title,
                finding.reason,
                finding.suggestion,
            ]
        )
    return output.getvalue()

