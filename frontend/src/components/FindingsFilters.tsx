import { RotateCcw } from "lucide-react";
import type { Finding } from "../types/analysis";
import type { FindingTypeFilter, SeverityFilter } from "../utils/findings";
import { findingTypeLabel, findingTypeOrder, severityLabel } from "../utils/labels";

interface FindingsFiltersProps {
  findings: Finding[];
  severityFilter: SeverityFilter;
  typeFilter: FindingTypeFilter;
  filteredCount: number;
  onSeverityChange: (value: SeverityFilter) => void;
  onTypeChange: (value: FindingTypeFilter) => void;
  onReset: () => void;
}

function uniqueFindingTypes(findings: Finding[]): string[] {
  const types = Array.from(new Set(findings.map((finding) => finding.type)));
  return types.sort((left, right) => {
    const leftIndex = findingTypeOrder.indexOf(left as (typeof findingTypeOrder)[number]);
    const rightIndex = findingTypeOrder.indexOf(right as (typeof findingTypeOrder)[number]);
    if (leftIndex === -1 && rightIndex === -1) return left.localeCompare(right);
    if (leftIndex === -1) return 1;
    if (rightIndex === -1) return -1;
    return leftIndex - rightIndex;
  });
}

export function FindingsFilters({
  findings,
  severityFilter,
  typeFilter,
  filteredCount,
  onSeverityChange,
  onTypeChange,
  onReset
}: FindingsFiltersProps) {
  const typeOptions = uniqueFindingTypes(findings);
  const hasActiveFilter = severityFilter !== "ALL" || typeFilter !== "ALL";

  return (
    <div className="filters-panel" aria-label="편집 필요 구간 필터">
      <div className="filters-grid">
        <label className="field">
          심각도
          <select
            value={severityFilter}
            onChange={(event) => onSeverityChange(event.currentTarget.value as SeverityFilter)}
          >
            <option value="ALL">전체</option>
            <option value="HIGH">{severityLabel.HIGH}</option>
            <option value="MEDIUM">{severityLabel.MEDIUM}</option>
            <option value="LOW">{severityLabel.LOW}</option>
            <option value="INFO">{severityLabel.INFO}</option>
          </select>
        </label>
        <label className="field">
          유형
          <select value={typeFilter} onChange={(event) => onTypeChange(event.currentTarget.value)}>
            <option value="ALL">전체</option>
            {typeOptions.map((type) => (
              <option key={type} value={type}>
                {findingTypeLabel[type] ?? type}
              </option>
            ))}
          </select>
        </label>
        <div className="filter-count" aria-live="polite">
          표시 중 {filteredCount}개 / 전체 {findings.length}개
        </div>
        <button type="button" className="secondary-button" onClick={onReset} disabled={!hasActiveFilter}>
          <RotateCcw aria-hidden="true" />
          필터 초기화
        </button>
      </div>
    </div>
  );
}
