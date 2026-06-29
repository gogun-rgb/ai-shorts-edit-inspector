from __future__ import annotations

from pathlib import Path

from app.models.analysis import Scene


def detect_scenes(video_path: Path, duration: float, threshold: float = 27.0) -> tuple[list[Scene], str | None]:
    try:
        from scenedetect import SceneManager, open_video
        from scenedetect.detectors import ContentDetector
    except Exception as exc:  # pragma: no cover - depends on optional runtime package.
        fallback = [Scene(index=0, start=0, end=duration, duration=duration)]
        return fallback, f"PySceneDetect를 초기화하지 못해 전체 영상을 단일 장면으로 처리했습니다: {exc}"

    try:
        video = open_video(str(video_path))
        manager = SceneManager()
        manager.add_detector(ContentDetector(threshold=threshold))
        manager.detect_scenes(video)
        scene_list = manager.get_scene_list()
    except Exception as exc:  # pragma: no cover - integration behavior.
        fallback = [Scene(index=0, start=0, end=duration, duration=duration)]
        return fallback, f"장면 분석에 실패해 전체 영상을 단일 장면으로 처리했습니다: {exc}"

    if not scene_list:
        return [Scene(index=0, start=0, end=duration, duration=duration)], None

    scenes: list[Scene] = []
    for index, (start_time, end_time) in enumerate(scene_list):
        start = round(start_time.get_seconds(), 3)
        end = round(min(end_time.get_seconds(), duration), 3)
        if end > start:
            scenes.append(Scene(index=index, start=start, end=end, duration=round(end - start, 3)))
    return scenes or [Scene(index=0, start=0, end=duration, duration=duration)], None

