import { FileVideo, FolderOpen, Upload } from "lucide-react";
import { useRef, useState } from "react";
import type { FormEvent } from "react";

interface VideoUploaderProps {
  onSubmit: (video: File, subtitle: File | null, settings: UploadSettings) => Promise<void> | void;
  busy?: boolean;
}

export interface UploadSettings {
  language: string;
  silenceThresholdDb: number;
  minSilenceDuration: number;
  longSceneSeconds: number;
}

const defaultSettings: UploadSettings = {
  language: "",
  silenceThresholdDb: -35,
  minSilenceDuration: 0.8,
  longSceneSeconds: 6
};

function firstFile(files: FileList | null | undefined): File | undefined {
  if (!files || files.length === 0) return undefined;
  return files.item?.(0) ?? files[0];
}

export function VideoUploader({ onSubmit, busy = false }: VideoUploaderProps) {
  const [video, setVideo] = useState<File | null>(null);
  const [subtitle, setSubtitle] = useState<File | null>(null);
  const [settings, setSettings] = useState<UploadSettings>(defaultSettings);
  const [error, setError] = useState<string | null>(null);
  const videoInputRef = useRef<HTMLInputElement | null>(null);

  function handleVideo(file: File | undefined) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".mp4")) {
      setVideo(null);
      setError("MP4 파일만 업로드할 수 있습니다.");
      return;
    }
    setError(null);
    setVideo(file);
  }

  function handleSubtitle(file: File | undefined) {
    if (!file) {
      setSubtitle(null);
      return;
    }
    const lower = file.name.toLowerCase();
    if (!lower.endsWith(".srt") && !lower.endsWith(".vtt")) {
      setError("자막 파일은 SRT 또는 VTT만 지원합니다.");
      setSubtitle(null);
      return;
    }
    setError(null);
    setSubtitle(file);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!video) return;
    await onSubmit(video, subtitle, settings);
  }

  return (
    <form className="upload-panel" onSubmit={handleSubmit}>
      <label
        className="drop-zone"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          handleVideo(event.dataTransfer.files.item(0) ?? undefined);
        }}
      >
        <FileVideo aria-hidden="true" />
        <span className="drop-title">MP4 영상을 끌어오거나 선택하세요</span>
        <span className="drop-copy">최대 500MB, 180초 이하 기준으로 분석합니다.</span>
        <input
          ref={videoInputRef}
          type="file"
          accept="video/mp4,.mp4"
          onChange={(event) => handleVideo(firstFile(event.currentTarget.files))}
        />
      </label>

      <div className="file-row">
        <button type="button" className="secondary-button" onClick={() => videoInputRef.current?.click()}>
          <FolderOpen aria-hidden="true" />
          파일 선택
        </button>
        <span className="file-name">{video ? video.name : "선택된 MP4가 없습니다."}</span>
      </div>

      <label className="field">
        선택 자막 파일
        <input
          type="file"
          accept=".srt,.vtt,text/vtt"
          onChange={(event) => handleSubtitle(firstFile(event.currentTarget.files))}
        />
      </label>
      {subtitle ? <p className="hint">자막 비교: {subtitle.name}</p> : <p className="hint">자막 파일이 없으면 transcript만 표시합니다.</p>}

      <div className="settings-grid">
        <label className="field">
          언어
          <select
            value={settings.language}
            onChange={(event) => setSettings({ ...settings, language: event.currentTarget.value })}
          >
            <option value="">자동 감지</option>
            <option value="ko">한국어</option>
            <option value="en">영어</option>
            <option value="ja">일본어</option>
          </select>
        </label>
        <label className="field">
          무음 dB
          <input
            type="number"
            value={settings.silenceThresholdDb}
            onChange={(event) => setSettings({ ...settings, silenceThresholdDb: Number(event.currentTarget.value) })}
          />
        </label>
        <label className="field">
          최소 무음
          <input
            type="number"
            step="0.1"
            value={settings.minSilenceDuration}
            onChange={(event) => setSettings({ ...settings, minSilenceDuration: Number(event.currentTarget.value) })}
          />
        </label>
        <label className="field">
          긴 장면 기준
          <input
            type="number"
            step="0.5"
            value={settings.longSceneSeconds}
            onChange={(event) => setSettings({ ...settings, longSceneSeconds: Number(event.currentTarget.value) })}
          />
        </label>
      </div>

      {error ? <p className="inline-error">{error}</p> : null}

      <button className="primary-button" type="submit" disabled={!video || busy}>
        <Upload aria-hidden="true" />
        {busy ? "분석 요청 중" : "분석 시작"}
      </button>
    </form>
  );
}
