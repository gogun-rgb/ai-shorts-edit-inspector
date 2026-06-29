from __future__ import annotations

import importlib.util
import platform
import shutil
import subprocess
import sys


def command_version(command: str) -> str:
    path = shutil.which(command)
    if path is None:
        return "missing"
    try:
        result = subprocess.run(
            [path, "-version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
        )
        first_line = (result.stdout or result.stderr).splitlines()[0]
        return f"{first_line} ({path})"
    except Exception as exc:
        return f"found at {path}, version check failed: {exc}"


def node_version(command: str) -> str:
    path = shutil.which(command)
    if path is None:
        return "missing"
    result = subprocess.run([path, "--version"], check=False, capture_output=True, text=True, timeout=8)
    return f"{result.stdout.strip()} ({path})"


def package_status(package: str) -> str:
    return "ok" if importlib.util.find_spec(package) else "missing"


def main() -> int:
    print(f"OS: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"Node.js: {node_version('node')}")
    print(f"npm: {node_version('npm.cmd' if platform.system() == 'Windows' else 'npm')}")
    print(f"FFmpeg: {command_version('ffmpeg')}")
    print(f"ffprobe: {command_version('ffprobe')}")
    for package in ["fastapi", "uvicorn", "faster_whisper", "scenedetect", "cv2", "pytest"]:
        print(f"Python package {package}: {package_status(package)}")
    print("Whisper model: base (override with WHISPER_MODEL)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

