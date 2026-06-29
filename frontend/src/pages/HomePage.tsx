import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createAnalysis } from "../api/client";
import { SettingsPanel } from "../components/SettingsPanel";
import { VideoUploader } from "../components/VideoUploader";
import type { UploadSettings } from "../components/VideoUploader";

export function HomePage() {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(video: File, subtitle: File | null, settings: UploadSettings) {
    setBusy(true);
    setError(null);
    try {
      const result = await createAnalysis({
        video,
        subtitle,
        language: settings.language || undefined,
        silenceThresholdDb: settings.silenceThresholdDb,
        minSilenceDuration: settings.minSilenceDuration,
        longSceneSeconds: settings.longSceneSeconds
      });
      navigate(`/analyses/${result.analysisId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "분석 요청에 실패했습니다.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="home-layout">
      <section className="intro-panel">
        <p className="eyebrow">Local-first video review</p>
        <h1>Shorts Edit Inspector</h1>
        <p className="lead">
          쇼츠, 릴스, 틱톡 초안에서 무음, 긴 장면, 빠른 컷, transcript와 자막 공백 후보를 한 타임라인으로 확인합니다.
        </p>
        <p className="disclaimer">
          이 분석 결과는 자동 편집 보조를 위한 규칙 기반 진단이며, 최종 편집 판단은 사용자가 내려야 합니다.
        </p>
      </section>

      <section className="workspace-grid">
        <VideoUploader onSubmit={handleSubmit} busy={busy} />
        <SettingsPanel />
      </section>

      {error ? <p className="inline-error wide">{error}</p> : null}
    </main>
  );
}

