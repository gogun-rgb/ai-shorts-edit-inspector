import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { FindingsTimeline } from "../components/FindingsTimeline";
import type { Finding } from "../types/analysis";
import { buildTimelineItems, playbackPercent } from "../utils/timeline";

const findings: Finding[] = [
  {
    id: "silence",
    type: "SILENCE",
    severity: "HIGH",
    start: 10,
    end: 20,
    duration: 10,
    title: "무음",
    reason: "무음",
    suggestion: "정리",
    source: "test",
    metadata: {}
  },
  {
    id: "scene",
    type: "LONG_SCENE",
    severity: "MEDIUM",
    start: 15,
    end: 30,
    duration: 15,
    title: "긴 장면",
    reason: "장면",
    suggestion: "확인",
    source: "test",
    metadata: {}
  }
];

describe("timeline calculations", () => {
  it("calculates start position, width, and lanes", () => {
    const items = buildTimelineItems(findings, 100);
    expect(items[0]).toMatchObject({ leftPercent: 10, widthPercent: 10, lane: 0 });
    expect(items[1]).toMatchObject({ leftPercent: 15, widthPercent: 15, lane: 1 });
  });

  it("handles zero duration without throwing", () => {
    expect(buildTimelineItems(findings, 0)[0]).toMatchObject({ leftPercent: 0, widthPercent: 0 });
    expect(playbackPercent(5, 0)).toBe(0);
  });
});

describe("FindingsTimeline", () => {
  it("renders a timeline item for each finding", () => {
    render(
      <FindingsTimeline
        findings={findings}
        videoDuration={100}
        currentTime={25}
        selectedId={null}
        onSeek={vi.fn()}
      />
    );

    expect(screen.getByTestId("timeline-segment-silence")).toBeInTheDocument();
    expect(screen.getByTestId("timeline-segment-scene")).toBeInTheDocument();
    expect(screen.getByTestId("timeline-playhead")).toHaveStyle({ left: "25%" });
  });

  it("calls onSeek when a timeline item is clicked", async () => {
    const user = userEvent.setup();
    const onSeek = vi.fn();
    render(
      <FindingsTimeline
        findings={findings}
        videoDuration={100}
        currentTime={0}
        selectedId={null}
        onSeek={onSeek}
      />
    );

    await user.click(screen.getByTestId("timeline-segment-silence"));
    expect(onSeek).toHaveBeenCalledWith(findings[0]);
  });

  it("marks the selected finding", () => {
    render(
      <FindingsTimeline
        findings={findings}
        videoDuration={100}
        currentTime={0}
        selectedId="scene"
        onSeek={vi.fn()}
      />
    );

    expect(screen.getByTestId("timeline-segment-scene")).toHaveClass("selected");
  });

  it("renders an empty state when there are no findings", () => {
    render(
      <FindingsTimeline
        findings={[]}
        videoDuration={100}
        currentTime={0}
        selectedId={null}
        onSeek={vi.fn()}
      />
    );

    expect(screen.getByText("검출된 편집 필요 구간이 없습니다.")).toBeInTheDocument();
  });
});

