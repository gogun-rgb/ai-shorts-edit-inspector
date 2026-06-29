from __future__ import annotations


def clamp_time(value: float, duration: float | None = None) -> float:
    value = max(0.0, float(value))
    if duration is not None:
        value = min(value, max(0.0, float(duration)))
    return round(value, 3)


def format_timestamp(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    minutes = int(seconds // 60)
    remaining = seconds - minutes * 60
    return f"{minutes:02d}:{remaining:05.2f}"

