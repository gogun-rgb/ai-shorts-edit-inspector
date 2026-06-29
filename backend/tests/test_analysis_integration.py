from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from app.main import create_app
from app.models.analysis import AnalysisStatus
from app.models.transcript import TranscriptResult, TranscriptSegment
from app.services import analysis_service


def _generate_test_video(output_path: Path) -> None:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=320x568:d=4",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=16000:cl=mono",
        "-shortest",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        str(output_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def _wait_for_done(client: TestClient, analysis_id: str) -> dict[str, Any]:
    done_statuses = {AnalysisStatus.COMPLETED, AnalysisStatus.PARTIAL_SUCCESS, AnalysisStatus.FAILED}
    for _ in range(30):
        response = client.get(f"/api/analyses/{analysis_id}")
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] in done_statuses:
            return payload
        time.sleep(0.1)
    raise AssertionError("analysis did not complete")


def test_real_mp4_analysis_api_flow(tmp_path: Path, monkeypatch) -> None:
    storage_dir = tmp_path / "analyses"
    video_path = tmp_path / "sample.mp4"
    transcript_calls: list[Path] = []

    monkeypatch.setenv("STORAGE_DIR", str(storage_dir))
    analysis_service._ANALYSES.clear()

    def fake_transcribe_video(
        video_path: Path,
        model_name: str,
        device: str,
        compute_type: str,
        language: str | None = None,
    ) -> TranscriptResult:
        transcript_calls.append(video_path)
        return TranscriptResult(
            language=language or "ko",
            languageProbability=1.0,
            duration=4.0,
            segments=[TranscriptSegment(id=0, start=0.5, end=1.2, text="테스트 음성")],
        )

    monkeypatch.setattr(analysis_service, "transcribe_video", fake_transcribe_video)

    try:
        _generate_test_video(video_path)
        app = create_app()
        with TestClient(app) as client, video_path.open("rb") as handle:
            created = client.post(
                "/api/analyses",
                files={"video": ("sample.mp4", handle, "video/mp4")},
                data={"language": "ko", "minSilenceDuration": "0.5", "longSceneSeconds": "1.0"},
            )
            assert created.status_code == 200
            analysis_id = created.json()["analysisId"]
            assert analysis_id

            final = _wait_for_done(client, analysis_id)
            assert final["status"] in {AnalysisStatus.COMPLETED, AnalysisStatus.PARTIAL_SUCCESS}
            assert transcript_calls, "Whisper transcription should be replaced by the test stub"
            assert final["metadata"]["duration"] > 3.5
            assert final["metadata"]["duration"] < 4.5
            assert final["metadata"]["hasAudio"] is True
            assert final["summary"]["totalFindings"] == len(final["findings"])
            assert isinstance(final["findings"], list)
            assert isinstance(final["scenes"], list)
            assert final["transcript"]["segments"][0]["text"] == "테스트 음성"

            json_export = client.get(f"/api/analyses/{analysis_id}/export/json")
            assert json_export.status_code == 200
            exported_json = json_export.json()
            assert exported_json["analysisId"] == analysis_id
            assert "summary" in exported_json

            csv_export = client.get(f"/api/analyses/{analysis_id}/export/csv")
            assert csv_export.status_code == 200
            assert csv_export.text.splitlines()[0] == "start,end,type,severity,title,reason,suggestion"

            video_response = client.get(f"/api/analyses/{analysis_id}/video")
            assert video_response.status_code == 200
            assert video_response.headers["content-type"].startswith("video/mp4")
            assert len(video_response.content) > 0

            deleted = client.delete(f"/api/analyses/{analysis_id}")
            assert deleted.status_code == 200
            assert deleted.json() == {"deleted": True}

            missing = client.get(f"/api/analyses/{analysis_id}")
            assert missing.status_code == 404
    finally:
        analysis_service._ANALYSES.clear()
