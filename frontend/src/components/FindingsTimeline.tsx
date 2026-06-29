import type { CSSProperties } from "react";
import type { Finding } from "../types/analysis";
import { buildTimelineItems, playbackPercent } from "../utils/timeline";
import { findingTypeLabel, severityLabel } from "../utils/labels";
import { formatTime } from "../utils/time";

interface FindingsTimelineProps {
  findings: Finding[];
  videoDuration: number;
  currentTime: number;
  selectedId?: string | null;
  onSeek: (finding: Finding) => void;
}

export function FindingsTimeline({
  findings,
  videoDuration,
  currentTime,
  selectedId,
  onSeek
}: FindingsTimelineProps) {
  if (findings.length === 0) {
    return <p className="empty-copy">검출된 편집 필요 구간이 없습니다.</p>;
  }

  const items = buildTimelineItems(findings, videoDuration);
  const laneCount = Math.max(1, ...items.map((item) => item.lane + 1));
  const playheadLeft = playbackPercent(currentTime, videoDuration);
  const ticks = [0, 25, 50, 75, 100];
  const safeDuration = Number.isFinite(videoDuration) && videoDuration > 0 ? videoDuration : 0;

  return (
    <div className="timeline-wrap" aria-label="편집 필요 구간 타임라인">
      <div className="timeline-scale" aria-hidden="true">
        <span>{formatTime(0)}</span>
        <span>{formatTime(safeDuration)}</span>
      </div>
      <div className="timeline-scroll">
        <div className="timeline-track" style={{ minHeight: `${laneCount * 34 + 34}px` }}>
          {ticks.map((tick) => (
            <span
              key={tick}
              className="timeline-tick"
              style={{ left: `${tick}%` }}
              aria-hidden="true"
            >
              {formatTime((safeDuration * tick) / 100)}
            </span>
          ))}
          <span
            className="timeline-playhead"
            style={{ left: `${playheadLeft}%` }}
            aria-label={`현재 재생 위치 ${formatTime(currentTime)}`}
            data-testid="timeline-playhead"
          />
          {items.map((item) => {
            const label = findingTypeLabel[item.finding.type] ?? item.finding.type;
            const severity = severityLabel[item.finding.severity];
            const style = {
              left: `${item.leftPercent}%`,
              width: `${item.widthPercent}%`,
              top: `${item.lane * 34 + 22}px`
            } satisfies CSSProperties;
            return (
              <button
                key={item.finding.id}
                type="button"
                className={`timeline-segment severity-${item.finding.severity.toLowerCase()} ${
                  selectedId === item.finding.id ? "selected" : ""
                }`}
                style={style}
                title={`${label} · ${severity} · ${formatTime(item.finding.start)} - ${formatTime(item.finding.end)}`}
                aria-label={`${label}, 심각도 ${severity}, ${formatTime(item.finding.start)}부터 ${formatTime(
                  item.finding.end
                )}까지 보기`}
                data-testid={`timeline-segment-${item.finding.id}`}
                onClick={() => onSeek(item.finding)}
              >
                <span>{severity}</span>
                <strong>{label}</strong>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

