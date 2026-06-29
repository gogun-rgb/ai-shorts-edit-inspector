from app.models.findings import Finding, FindingType, Severity
from app.models.transcript import SubtitleCue, TranscriptSegment
from app.services.report_service import calculate_readiness_score, merge_similar_findings
from app.services.subtitle_service import transcript_segments_without_subtitle


def make_finding(start: float, end: float, finding_type: FindingType = FindingType.SILENCE) -> Finding:
    return Finding(
        id=f"{finding_type}-{start}",
        type=finding_type,
        severity=Severity.MEDIUM,
        start=start,
        end=end,
        duration=end - start,
        title="test",
        reason="reason",
        suggestion="suggestion",
        source="test",
    )


def test_merge_overlapping_same_type_findings() -> None:
    merged = merge_similar_findings([make_finding(1, 3), make_finding(1.1, 3.1)], video_duration=5)
    assert len(merged) == 1
    assert merged[0].start == 1
    assert merged[0].end == 3.1


def test_keep_different_types_when_overlapping() -> None:
    merged = merge_similar_findings(
        [make_finding(1, 3), make_finding(1.1, 3.1, FindingType.LONG_SCENE)],
        video_duration=5,
    )
    assert len(merged) == 2


def test_score_bounds() -> None:
    many_findings = [make_finding(index, index + 1) for index in range(30)]
    assert calculate_readiness_score([]) == 100
    assert calculate_readiness_score(many_findings) == 0


def test_transcript_subtitle_gap_detection() -> None:
    segments = [
        TranscriptSegment(id=0, start=0.0, end=1.0, text="covered"),
        TranscriptSegment(id=1, start=2.0, end=4.0, text="missing"),
    ]
    cues = [SubtitleCue(index=0, start=0.0, end=1.1, text="covered")]
    missing = transcript_segments_without_subtitle(segments, cues, tolerance=0.3)
    assert [segment.text for segment in missing] == ["missing"]

