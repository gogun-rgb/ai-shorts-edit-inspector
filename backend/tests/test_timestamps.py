from app.utils.timestamps import clamp_time, format_timestamp


def test_format_timestamp() -> None:
    assert format_timestamp(3.2) == "00:03.20"
    assert format_timestamp(65.456) == "01:05.46"


def test_clamp_time() -> None:
    assert clamp_time(-2.0, 10.0) == 0.0
    assert clamp_time(11.2, 10.0) == 10.0

