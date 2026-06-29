import type { Finding } from "../types/analysis";
import type { Severity } from "../types/analysis";

export type SeverityFilter = "ALL" | Severity;
export type FindingTypeFilter = "ALL" | string;

export function filterFindings(
  findings: Finding[],
  severityFilter: SeverityFilter,
  typeFilter: FindingTypeFilter
): Finding[] {
  return findings.filter((finding) => {
    const severityMatches = severityFilter === "ALL" || finding.severity === severityFilter;
    const typeMatches = typeFilter === "ALL" || finding.type === typeFilter;
    return severityMatches && typeMatches;
  });
}
