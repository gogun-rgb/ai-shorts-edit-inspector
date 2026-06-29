import type { AnalysisResult } from "../types/analysis";
import { formatTime } from "../utils/time";

interface SummaryCardsProps {
  result: AnalysisResult;
}

export function SummaryCards({ result }: SummaryCardsProps) {
  const metadata = result.metadata;
  const summary = result.summary;
  if (!metadata || !summary) return null;

  return (
    <section className="summary-grid" aria-label="분석 요약">
      <article className="metric strong">
        <span>편집 준비도</span>
        <strong>{summary.readinessScore}</strong>
        <small>{summary.grade}</small>
      </article>
      <article className="metric">
        <span>영상 길이</span>
        <strong>{formatTime(metadata.duration)}</strong>
        <small>{metadata.width}x{metadata.height}</small>
      </article>
      <article className="metric">
        <span>화면 비율</span>
        <strong>{metadata.aspectRatio.toFixed(3)}</strong>
        <small>{metadata.hasAudio ? "오디오 있음" : "오디오 없음"}</small>
      </article>
      <article className="metric">
        <span>발견 항목</span>
        <strong>{summary.totalFindings}</strong>
        <small>높음 {summary.highCount}개</small>
      </article>
    </section>
  );
}

