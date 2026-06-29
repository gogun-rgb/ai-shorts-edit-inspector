import { Play } from "lucide-react";
import type { Finding } from "../types/analysis";
import { findingTypeLabel, severityLabel } from "../utils/labels";
import { formatTime } from "../utils/time";

interface FindingsTableProps {
  findings: Finding[];
  selectedId?: string | null;
  onSeek: (finding: Finding) => void;
}

export function FindingsTable({ findings, selectedId, onSeek }: FindingsTableProps) {
  if (findings.length === 0) {
    return <p className="empty-copy">편집 확인이 필요한 구간이 감지되지 않았습니다.</p>;
  }

  return (
    <div className="table-wrap">
      <table className="findings-table">
        <thead>
          <tr>
            <th>시작</th>
            <th>종료</th>
            <th>유형</th>
            <th>심각도</th>
            <th>감지 이유</th>
            <th>편집 제안</th>
            <th>보기</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((finding) => (
            <tr
              key={finding.id}
              className={finding.id === selectedId ? "selected" : ""}
              onClick={() => onSeek(finding)}
            >
              <td>{formatTime(finding.start)}</td>
              <td>{formatTime(finding.end)}</td>
              <td>{findingTypeLabel[finding.type] ?? finding.type}</td>
              <td>
                <span className={`severity severity-${finding.severity.toLowerCase()}`}>
                  {severityLabel[finding.severity]}
                </span>
              </td>
              <td>{finding.reason}</td>
              <td>{finding.suggestion}</td>
              <td>
                <button
                  type="button"
                  className="icon-button"
                  aria-label={`${formatTime(finding.start)} 구간 보기`}
                  onClick={(event) => {
                    event.stopPropagation();
                    onSeek(finding);
                  }}
                >
                  <Play aria-hidden="true" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

