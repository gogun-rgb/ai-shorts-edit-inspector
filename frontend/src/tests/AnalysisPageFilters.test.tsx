import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { AnalysisPage } from "../pages/AnalysisPage";
import type { AnalysisResult } from "../types/analysis";

const result: AnalysisResult = {
  analysisId: "123",
  status: "COMPLETED",
  createdAt: new Date().toISOString(),
  completedAt: new Date().toISOString(),
  currentStep: "COMPLETED",
  metadata: {
    fileName: "source.mp4",
    fileSizeBytes: 100,
    duration: 20,
    width: 1080,
    height: 1920,
    aspectRatio: 0.5625,
    fps: 30,
    videoCodec: "h264",
    audioCodec: "aac",
    hasAudio: true,
    averageBitrate: 1000
  },
  summary: {
    readinessScore: 82,
    grade: "Minor fixes",
    totalFindings: 2,
    highCount: 1,
    mediumCount: 1,
    lowCount: 0,
    infoCount: 0
  },
  findings: [
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
      start: 8,
      end: 15,
      duration: 7,
      title: "긴 장면",
      reason: "장면",
      suggestion: "확인",
      source: "test",
      metadata: {}
    }
  ],
  transcript: {
    language: "ko",
    languageProbability: 0.9,
    duration: 20,
    segments: [],
    error: null
  },
  scenes: [{ index: 0, start: 0, end: 20, duration: 20 }],
  warnings: [],
  error: null
};

function renderAnalysisPage() {
  vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok: true,
    json: async () => result
  } as Response);

  render(
    <MemoryRouter initialEntries={["/analyses/123"]}>
      <Routes>
        <Route path="/analyses/:analysisId" element={<AnalysisPage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("AnalysisPage filters", () => {
  beforeEach(() => {
    vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue(undefined);
    Object.defineProperty(Element.prototype, "scrollIntoView", {
      configurable: true,
      value: vi.fn()
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders filter controls before the timeline and findings table", async () => {
    renderAnalysisPage();

    const filters = await screen.findByRole("heading", { name: "결과 필터" });
    const timeline = screen.getByRole("heading", { name: "타임라인" });
    const table = screen.getByRole("heading", { name: "편집 필요 구간" });

    expect(filters.compareDocumentPosition(timeline) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(timeline.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("clears the selected finding when active filters hide it", async () => {
    const user = userEvent.setup();
    renderAnalysisPage();

    const highSegment = await screen.findByTestId("timeline-segment-high-silence");
    await user.click(highSegment);
    expect(highSegment).toHaveClass("selected");

    await user.selectOptions(screen.getByLabelText("심각도"), "MEDIUM");

    await waitFor(() => expect(screen.queryByTestId("timeline-segment-high-silence")).not.toBeInTheDocument());
    expect(screen.getByTestId("timeline-segment-medium-scene")).not.toHaveClass("selected");

    await user.click(screen.getByRole("button", { name: "필터 초기화" }));

    const restoredHighSegment = await screen.findByTestId("timeline-segment-high-silence");
    expect(restoredHighSegment).not.toHaveClass("selected");
  });

  it("keeps the selected finding when filters still include it", async () => {
    const user = userEvent.setup();
    renderAnalysisPage();

    const highSegment = await screen.findByTestId("timeline-segment-high-silence");
    await user.click(highSegment);
    expect(highSegment).toHaveClass("selected");

    await user.selectOptions(screen.getByLabelText("유형"), "SILENCE");

    expect(await screen.findByTestId("timeline-segment-high-silence")).toHaveClass("selected");
  });
});
