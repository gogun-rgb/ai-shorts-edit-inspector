from app.models.analysis import Scene
from app.models.findings import FindingType, Severity
from app.services.report_service import build_scene_findings


def test_long_and_very_long_scene_detection() -> None:
    scenes = [
        Scene(index=0, start=0, end=6.2, duration=6.2),
        Scene(index=1, start=6.2, end=17.0, duration=10.8),
    ]
    findings = build_scene_findings(scenes, 6.0, 10.0, 0.45, 3.0, 4, 20.0)
    assert findings[0].type == FindingType.LONG_SCENE
    assert findings[0].severity == Severity.MEDIUM
    assert findings[1].type == FindingType.VERY_LONG_SCENE
    assert findings[1].severity == Severity.HIGH


def test_rapid_cuts_detection() -> None:
    scenes = [
        Scene(index=0, start=0.0, end=0.3, duration=0.3),
        Scene(index=1, start=0.3, end=0.7, duration=0.4),
        Scene(index=2, start=0.7, end=1.0, duration=0.3),
        Scene(index=3, start=1.0, end=1.3, duration=0.3),
    ]
    findings = build_scene_findings(scenes, 6.0, 10.0, 0.45, 3.0, 4, 5.0)
    assert any(finding.type == FindingType.RAPID_CUTS for finding in findings)


def test_single_short_cut_is_low_only() -> None:
    scenes = [Scene(index=0, start=0.0, end=0.3, duration=0.3)]
    findings = build_scene_findings(scenes, 6.0, 10.0, 0.45, 3.0, 4, 5.0)
    assert len(findings) == 1
    assert findings[0].type == FindingType.SHORT_SCENE
    assert findings[0].severity == Severity.LOW

