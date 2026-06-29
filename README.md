# Shorts Edit Inspector

Shorts Edit Inspector is a local-first review tool for short-form video drafts.

It is not a simple upload UI. It combines FFmpeg silence detection, ffprobe metadata, Whisper transcript output, optional subtitle timestamps, and PySceneDetect scene boundaries into one review timeline. Clicking a finding seeks the real video to that timestamp. Core features run locally without paid AI APIs, and findings can be exported as JSON or CSV.

> 이 분석 결과는 자동 편집 보조를 위한 규칙 기반 진단이며, 최종 편집 판단은 사용자가 내려야 합니다.

## Problem

Beginner creators often know a short-form video feels slow or jumpy, but they do not yet know where to inspect the edit. This app points to measurable moments: long silence, long single scenes, rapid short cuts, aspect ratio issues, transcript segments, and possible subtitle gaps when an SRT/VTT file is provided.

The app does not claim to understand editing quality perfectly. It reports rule-based signals and keeps the final decision with the editor.

## Target Users

- First-time Shorts, Reels, and TikTok creators
- Editors checking rough cuts before posting
- Portfolio reviewers who want to see a practical local video pipeline

## Features

- MP4 upload with UUID-based local storage
- ffprobe metadata extraction
- FFmpeg `silencedetect` parsing
- faster-whisper transcript generation with partial-success handling
- PySceneDetect scene detection
- Long scene, very long scene, short cut, and rapid-cut rules
- Optional SRT/VTT upload and transcript-to-subtitle gap comparison
- Readiness score and grade
- HTML5 video player with finding-row seek
- Severity and finding type filters with reset and visible result counts
- Interactive findings timeline with click-to-seek behavior
- Current playback position marker on the findings timeline
- JSON and CSV exports
- Delete API for temporary analysis files
- Backend and frontend tests
- GitHub Actions CI

## Signals Actually Analyzed

- Silence duration and position
- Scene duration
- Consecutive short scenes within a time window
- Transcript segment timestamps
- Optional subtitle cue timestamps
- Beginning and ending silence
- Aspect ratio
- Total duration

## What It Does Not Analyze

- It does not OCR burned-in captions.
- It does not judge creative quality.
- It does not detect whether a cut is objectively wrong.
- It does not require OpenAI, ElevenLabs, or another paid API.
- It does not upload videos to a cloud service by default.

## Tech Stack

Backend: Python 3.11+, FastAPI, Uvicorn, Pydantic, FFmpeg, ffprobe, faster-whisper, PySceneDetect, OpenCV headless, pytest, ruff.

Frontend: React, TypeScript, Vite, React Router, Vitest, React Testing Library, plain CSS, lucide-react icons.

## System Structure

```text
backend/app/api              FastAPI routes
backend/app/core             settings and user-facing errors
backend/app/models           Pydantic response models
backend/app/services         FFmpeg, metadata, transcript, scene, subtitle, report logic
backend/app/utils            path and timestamp helpers
frontend/src/api             typed API client
frontend/src/components      uploader, player, filters, timeline, findings, transcript, status UI
frontend/src/pages           home and analysis screens
frontend/src/utils           labels, finding filters, timeline calculations, time formatting
storage/analyses             local temporary analysis data
scripts                      dev and system check helpers
```

## Analysis Pipeline

1. Validate extension and MIME type.
2. Save the upload under a UUID analysis directory.
3. Verify the real file with ffprobe.
4. Extract metadata.
5. Run FFmpeg silence detection when audio exists.
6. Run faster-whisper transcript generation when audio exists.
7. Run PySceneDetect scene detection.
8. Apply rule-based findings.
9. Compare transcript with optional SRT/VTT cues.
10. Merge overlapping same-type findings.
11. Calculate readiness score.
12. Save `result.json` and expose exports.

## Detection Rules

Silence uses FFmpeg `silencedetect=n=-35dB:d=0.8` by default. Silence under 1.5s is low, 1.5s to 2.5s is medium, and 2.5s or longer is high. Beginning and ending silence get specific suggestions.

Transcript uses faster-whisper with `base`, CPU, and `int8` by default. If model download or initialization fails, the analysis can still complete as partial success and the UI shows the exact reason.

Scene detection uses PySceneDetect `ContentDetector`. Scenes of 6s or longer become review candidates; scenes of 10s or longer are high priority.

Rapid cuts are detected when at least 4 scenes shorter than 0.45s appear within a 3s window. A single short scene is only a low-priority candidate.

Subtitle gaps are detected only when a user uploads SRT/VTT. Transcript segments are compared with subtitle cues using a 0.3s tolerance. Without a subtitle file, the app only shows transcript segments as caption-production candidates.

## Result Filters and Timeline

The result screen can filter findings by severity and by finding type. The shared filter controls sit above both the timeline and the findings table, and the same filtered set is applied to both views. JSON and CSV exports continue to use the full original analysis result.

The interactive timeline maps each finding to the uploaded video's duration. A finding segment's horizontal position is based on `start / videoDuration`, and its width is based on `duration / videoDuration`. Very short findings get a minimum visible width so they remain clickable, but the underlying timestamps are not changed.

Clicking a timeline segment or a table row seeks the HTML5 video player to the finding start time. The selected finding is reflected in both the table and the timeline, and the playhead shows the current playback position. If a filter change hides the selected finding, the selection is cleared instead of leaving a stale highlighted state. These timeline markers are rule-based diagnostics and do not predict views, retention, or creative quality.

## Readiness Score

The score starts at 100 and subtracts points:

- High finding: -12
- Medium finding: -6
- Low finding: -2
- Beginning silence: extra -5
- Ending silence: extra -3
- Very long scene: extra -5
- Rapid-cut window: extra -5
- Subtitle gap: -3 to -8
- Aspect ratio warning: -8

Grades: `Ready` for 90-100, `Minor fixes` for 75-89, `Needs review` for 50-74, and `Major review` below 50.

## Windows Setup

Install FFmpeg and make sure both commands work:

```powershell
ffmpeg -version
ffprobe -version
```

Create and install the backend:

```powershell
cd ai-shorts-edit-inspector\backend
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
```

Install the frontend:

```powershell
cd ..\frontend
npm.cmd install
```

Run both dev servers:

```powershell
cd ..
.\scripts\run_dev.ps1
```

If you prefer manual terminals:

```powershell
cd ai-shorts-edit-inspector\backend
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

cd ai-shorts-edit-inspector\frontend
npm.cmd run dev
```

Stop servers by closing the two terminal windows or pressing `Ctrl+C` in each manual terminal.

## macOS/Linux Setup

```bash
cd ai-shorts-edit-inspector/backend
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

cd ../frontend
npm install

cd ..
./scripts/run_dev.sh
```

## Tests

Backend:

```powershell
cd ai-shorts-edit-inspector\backend
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m pytest
```

Backend tests include a real MP4 API integration test. The test generates a short temporary video with FFmpeg, uploads it through `POST /api/analyses`, lets ffprobe, FFmpeg silence detection, PySceneDetect, report generation, exports, video delivery, and deletion run through the API, and replaces only Whisper transcription with a fixed test transcript so CI does not download a model.

Frontend:

```powershell
cd ai-shorts-edit-inspector\frontend
npm.cmd run lint
npm.cmd run typecheck
npm.cmd test
npm.cmd run build
```

The frontend tests cover upload validation, partial-success warnings, findings table selection, severity/type filters, combined filter behavior, filter reset, the filter/timeline/table render order, clearing hidden selections, preserving visible selections, timeline calculations, timeline click-to-seek behavior, selected timeline items, empty states, and playback position rendering.

System check:

```powershell
cd ai-shorts-edit-inspector
backend\.venv\Scripts\python scripts\check_system.py
```

## Environment Variables

See [backend/.env.example](backend/.env.example).

Important settings:

- `MAX_UPLOAD_MB`
- `MAX_VIDEO_DURATION_SECONDS`
- `WHISPER_MODEL`
- `WHISPER_DEVICE`
- `WHISPER_COMPUTE_TYPE`
- `SILENCE_THRESHOLD_DB`
- `MIN_SILENCE_DURATION`
- `LONG_SCENE_SECONDS`
- `VERY_LONG_SCENE_SECONDS`
- `SHORT_SCENE_SECONDS`
- `RAPID_CUT_WINDOW_SECONDS`
- `RAPID_CUT_MIN_COUNT`

## API

- `GET /api/health`
- `POST /api/analyses`
- `GET /api/analyses/{analysis_id}`
- `GET /api/analyses/{analysis_id}/video`
- `GET /api/analyses/{analysis_id}/export/json`
- `GET /api/analyses/{analysis_id}/export/csv`
- `DELETE /api/analyses/{analysis_id}`

Upload fields:

- `video`: required MP4
- `subtitle`: optional SRT/VTT
- `language`: optional language code
- `silenceThresholdDb`: optional number
- `minSilenceDuration`: optional number
- `longSceneSeconds`: optional number

## Security Notes

- Original filenames are not trusted.
- Analysis directories use UUIDs.
- Stored paths are checked to stay under `storage/analyses`.
- Upload size and video duration limits are enforced.
- subprocess calls use argument arrays and do not use `shell=True`.
- `.env`, uploaded videos, generated audio, transcript output, and analysis JSON are ignored by Git.
- CORS is limited to local development origins.

## Known Limits

- Whisper may download a model on first real transcript run.
- CPU transcript generation can be slow.
- PySceneDetect can miss subtle cuts or split intentional motion.
- Burned-in captions are not OCR-scanned.
- Readiness score and timeline findings are rule-based review aids, not performance predictions.
- Browser autoplay may be blocked after seeking.
- CI should not depend on Whisper model downloads.

## v0.1.0 Changes

- Added severity-based filtering for findings.
- Added finding type filtering based on returned backend finding types.
- Added combined filters, result counts, and filter reset.
- Added an interactive findings timeline below the video player.
- Added current playback position visualization.
- Linked table and timeline selection state.
- Added frontend tests for filters and timeline interactions.
- Updated the GitHub workflow around Issues, PRs, CI, and Release preparation.

## v0.1.1 Changes

- Moved shared findings filters above the timeline and findings table.
- Clear the selected finding when it is excluded by active filters.
- Added a real MP4 API integration test using FFmpeg-generated media.
- Improved project management documentation.
- Replaced screenshot placeholders with an accurate demo media note.

## Project Management

No GitHub Project link is documented yet because the current GitHub CLI token cannot read or create Projects. `gh project list --owner gogun-rgb` fails with a missing `read:project` scope. Refresh the token before adding a verified Project link:

```powershell
gh auth refresh -h github.com -s project,read:project
```

## Future Improvements

- Markdown report export
- Per-video history database
- Caption OCR as an optional advanced mode
- User-tunable rule presets
- Persistent GitHub Project automation once the GitHub CLI token has project scope

## Demo Media

Screenshots and a short interaction GIF will be added separately.

Planned media:

- Upload screen
- Analysis progress
- Findings timeline and filters
- Transcript and scene panels

## License

MIT. See [LICENSE](LICENSE).
