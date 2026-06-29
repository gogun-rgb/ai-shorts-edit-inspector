import { Download, RotateCcw, Trash2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { deleteAnalysis, exportUrl, fetchAnalysis } from "../api/client";
import { AnalysisProgress } from "../components/AnalysisProgress";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { FindingsTable } from "../components/FindingsTable";
import { SummaryCards } from "../components/SummaryCards";
import { TranscriptPanel } from "../components/TranscriptPanel";
import { VideoPlayer } from "../components/VideoPlayer";
import type { VideoPlayerHandle } from "../components/VideoPlayer";
import type { AnalysisResult, Finding, TranscriptSegment } from "../types/analysis";
import { formatTime } from "../utils/time";

const doneStatuses = new Set(["COMPLETED", "PARTIAL_SUCCESS", "FAILED"]);

export function AnalysisPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const playerRef = useRef<VideoPlayerHandle | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    const id = analysisId;
    if (!id) return;
    let alive = true;

    async function load(idToFetch: string) {
      try {
        const next = await fetchAnalysis(idToFetch);
        if (!alive) return;
        setResult(next);
        setError(null);
        if (doneStatuses.has(next.status)) {
          window.clearInterval(timer);
        }
      } catch (err) {
        if (!alive) return;
        setError(err instanceof Error ? err.message : "분석 결과를 불러오지 못했습니다.");
      }
    }

    const timer = window.setInterval(() => void load(id), 1500);
    void load(id);
    return () => {
      alive = false;
      window.clearInterval(timer);
    };
  }, [analysisId]);

  if (!analysisId) return <ErrorState message="분석 ID가 없습니다." />;
  if (error) return <ErrorState message={error} />;
  if (!result) return <EmptyState />;

  const isDone = doneStatuses.has(result.status);

  function seekFinding(finding: Finding) {
    setSelectedId(finding.id);
    playerRef.current?.seekTo(finding.start);
  }

  function seekSegment(segment: TranscriptSegment) {
    playerRef.current?.seekTo(segment.start);
  }

  async function handleDelete() {
    if (!analysisId) return;
    await deleteAnalysis(analysisId);
    navigate("/");
  }

  return (
    <main className="analysis-layout">
      <header className="analysis-header">
        <div>
          <Link to="/" className="text-link">
            새 영상 분석
          </Link>
          <h1>분석 결과</h1>
        </div>
        <div className="action-row">
          <a className="secondary-button" href={exportUrl(analysisId, "json")}>
            <Download aria-hidden="true" />
            JSON
          </a>
          <a className="secondary-button" href={exportUrl(analysisId, "csv")}>
            <Download aria-hidden="true" />
            CSV
          </a>
          <button type="button" className="secondary-button" onClick={handleDelete}>
            <Trash2 aria-hidden="true" />
            삭제
          </button>
        </div>
      </header>

      {result.status === "FAILED" ? <ErrorState message={result.error ?? "분석이 실패했습니다."} /> : null}
      {!isDone ? <AnalysisProgress currentStep={result.currentStep} /> : null}
      {result.warnings.length > 0 ? (
        <section className="warnings-panel" aria-label="분석 경고">
          {result.status === "PARTIAL_SUCCESS" ? <strong>부분 성공</strong> : null}
          {result.warnings.map((warning) => (
            <p key={warning}>{warning}</p>
          ))}
        </section>
      ) : null}

      {result.metadata && result.summary ? (
        <>
          <SummaryCards result={result} />
          <VideoPlayer analysisId={analysisId} ref={playerRef} />
          <section className="panel">
            <div className="section-heading">
              <h2>편집 필요 구간</h2>
              <p>행을 선택하면 영상이 해당 시점으로 이동합니다.</p>
            </div>
            <FindingsTable findings={result.findings} selectedId={selectedId} onSeek={seekFinding} />
          </section>
          <section className="split-grid">
            <div className="panel">
              <div className="section-heading">
                <h2>Transcript</h2>
                <p>구간을 선택하면 영상으로 이동합니다.</p>
              </div>
              <TranscriptPanel transcript={result.transcript} onSeek={seekSegment} />
            </div>
            <div className="panel">
              <div className="section-heading">
                <h2>장면 목록</h2>
                <p>PySceneDetect 기준 장면 단위입니다.</p>
              </div>
              <div className="scene-list">
                {result.scenes.map((scene) => (
                  <button key={scene.index} type="button" onClick={() => playerRef.current?.seekTo(scene.start)}>
                    <span>Scene {scene.index + 1}</span>
                    <strong>{formatTime(scene.start)} - {formatTime(scene.end)}</strong>
                  </button>
                ))}
              </div>
            </div>
          </section>
        </>
      ) : (
        <section className="panel centered">
          <RotateCcw aria-hidden="true" />
          <h2>분석 결과 생성 중</h2>
          <p>현재 단계가 끝나면 영상 플레이어와 진단 표가 표시됩니다.</p>
        </section>
      )}
    </main>
  );
}
