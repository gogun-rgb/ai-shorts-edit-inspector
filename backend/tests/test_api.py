from fastapi.testclient import TestClient

from app.main import app
from app.utils.files import safe_uuid_name

client = TestClient(app)


def test_health_api() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ffmpegAvailable" in data
    assert "whisper" in data


def test_non_video_upload_rejected() -> None:
    response = client.post(
        "/api/analyses",
        files={"video": ("note.txt", b"not a video", "text/plain")},
    )
    assert response.status_code == 400


def test_safe_uuid_name_keeps_suffix_only() -> None:
    filename = safe_uuid_name("../../bad.mp4")
    assert filename.endswith(".mp4")
    assert ".." not in filename

