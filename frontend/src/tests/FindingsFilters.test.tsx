import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { FindingsFilters } from "../components/FindingsFilters";
import type { Finding } from "../types/analysis";
import { filterFindings } from "../utils/findings";

const findings: Finding[] = [
  {
    id: "high-silence",
    type: "SILENCE",
    severity: "HIGH",
    start: 1,
    end: 3,
    duration: 2,
    title: "긴 무음",
    reason: "무음",
    suggestion: "정리",
    source: "test",
    metadata: {}
  },
  {
    id: "medium-scene",
    type: "LONG_SCENE",
    severity: "MEDIUM",
    start: 4,
    end: 11,
    duration: 7,
    title: "긴 장면",
    reason: "장면",
    suggestion: "확인",
    source: "test",
    metadata: {}
  },
  {
    id: "low-duration",
    type: "VIDEO_DURATION",
    severity: "LOW",
    start: 0,
    end: 10,
    duration: 10,
    title: "영상 길이",
    reason: "길이",
    suggestion: "확인",
    source: "test",
    metadata: {}
  }
];

describe("filterFindings", () => {
  it("shows every finding by default", () => {
    expect(filterFindings(findings, "ALL", "ALL")).toHaveLength(3);
  });

  it("filters by severity", () => {
    expect(filterFindings(findings, "HIGH", "ALL").map((finding) => finding.id)).toEqual(["high-silence"]);
  });

  it("filters by type", () => {
    expect(filterFindings(findings, "ALL", "LONG_SCENE").map((finding) => finding.id)).toEqual(["medium-scene"]);
  });

  it("combines severity and type filters", () => {
    expect(filterFindings(findings, "HIGH", "LONG_SCENE")).toHaveLength(0);
  });
});

describe("FindingsFilters", () => {
  it("renders count text and reset action", async () => {
    const user = userEvent.setup();
    const onReset = vi.fn();
    render(
      <FindingsFilters
        findings={findings}
        severityFilter="HIGH"
        typeFilter="ALL"
        filteredCount={1}
        onSeverityChange={vi.fn()}
        onTypeChange={vi.fn()}
        onReset={onReset}
      />
    );

    expect(screen.getByText("표시 중 1개 / 전체 3개")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "필터 초기화" }));
    expect(onReset).toHaveBeenCalledTimes(1);
  });

  it("emits severity and type changes with accessible controls", async () => {
    const user = userEvent.setup();
    const onSeverityChange = vi.fn();
    const onTypeChange = vi.fn();
    render(
      <FindingsFilters
        findings={findings}
        severityFilter="ALL"
        typeFilter="ALL"
        filteredCount={3}
        onSeverityChange={onSeverityChange}
        onTypeChange={onTypeChange}
        onReset={vi.fn()}
      />
    );

    await user.selectOptions(screen.getByLabelText("심각도"), "MEDIUM");
    await user.selectOptions(screen.getByLabelText("유형"), "VIDEO_DURATION");
    expect(onSeverityChange).toHaveBeenCalledWith("MEDIUM");
    expect(onTypeChange).toHaveBeenCalledWith("VIDEO_DURATION");
  });
});
