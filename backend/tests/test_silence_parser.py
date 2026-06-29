from app.services.silence_detector import parse_silence_log


def test_parse_regular_silence_log() -> None:
    log = """
    [silencedetect @ 000] silence_start: 3.2
    [silencedetect @ 000] silence_end: 5.1 | silence_duration: 1.9
    """
    intervals = parse_silence_log(log, video_duration=10)
    assert len(intervals) == 1
    assert intervals[0].start == 3.2
    assert intervals[0].end == 5.1
    assert intervals[0].duration == 1.9


def test_parse_silence_until_end() -> None:
    intervals = parse_silence_log("silence_start: 7.5", video_duration=10)
    assert intervals[0].start == 7.5
    assert intervals[0].end == 10
    assert intervals[0].duration == 2.5


def test_ignore_invalid_silence_log() -> None:
    log = """
    silence_start: nope
    silence_end: -1 | silence_duration: -3
    silence_end: 2 | silence_duration: -1
    """
    assert parse_silence_log(log, video_duration=10) == []

