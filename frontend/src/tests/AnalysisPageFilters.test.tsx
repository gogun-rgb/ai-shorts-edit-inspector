import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
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
      title: "Long silence",
      reason: "Silence detected",
      suggestion: "Trim this section",
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
      title: "Long scene",
      reason: "Scene is long",
      suggestion: "Check pacing",
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

function renderAnalysisPage(responses: AnalysisResult[] = [result]) {
  let responseIndex = 0;
  vi.spyOn(globalThis, "fetch").mockImplementation(async () => {
    const response = responses[Math.min(responseIndex, responses.length - 1)];
    responseIndex += 1;
    return {
      ok: true,
      json: async () => response
    } as Response;
  });

  render(
    <MemoryRouter initialEntries={["/analyses/123"]}>
      <Routes>
        <Route path="/analyses/:analysisId" element={<AnalysisPage />} />
      </Routes>
    </MemoryRouter>
  );
}

function getSeveritySelect() {
  return screen.getAllByRole("combobox")[0];
}

function getTypeSelect() {
  return screen.getAllByRole("combobox")[1];
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

    const filters = await screen.findByTestId("findings-controls-section");
    const timeline = screen.getByTestId("timeline-section");
    const table = screen.getByTestId("findings-table-section");

    expect(filters.compareDocumentPosition(timeline) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(timeline.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("clears the selected finding when active filters hide it", async () => {
    const user = userEvent.setup();
    renderAnalysisPage();

    const highSegment = await screen.findByTestId("timeline-segment-high-silence");
    await user.click(highSegment);
    expect(highSegment).toHaveClass("selected");

    await user.selectOptions(getSeveritySelect(), "MEDIUM");

    await waitFor(() => expect(screen.queryByTestId("timeline-segment-high-silence")).not.toBeInTheDocument());
    expect(screen.getByTestId("timeline-segment-medium-scene")).not.toHaveClass("selected");

    await user.selectOptions(getSeveritySelect(), "ALL");

    const restoredHighSegment = await screen.findByTestId("timeline-segment-high-silence");
    expect(restoredHighSegment).not.toHaveClass("selected");
  });

  it("keeps the selected finding when filters still include it", async () => {
    const user = userEvent.setup();
    renderAnalysisPage();

    const highSegment = await screen.findByTestId("timeline-segment-high-silence");
    await user.click(highSegment);
    expect(highSegment).toHaveClass("selected");

    await user.selectOptions(getTypeSelect(), "SILENCE");

    expect(await screen.findByTestId("timeline-segment-high-silence")).toHaveClass("selected");
  });

  it("clears the selected finding when refreshed results move it outside active filters", async () => {
    const user = userEvent.setup();
    const pendingResult: AnalysisResult = {
      ...result,
      status: "DETECTING_SCENES",
      completedAt: null,
      currentStep: "DETECTING_SCENES"
    };
    const refreshedResult: AnalysisResult = {
      ...result,
      summary: {
        ...result.summary!,
        highCount: 0,
        mediumCount: 2
      },
      findings: [
        {
          ...result.findings[0],
          severity: "MEDIUM"
        },
        result.findings[1]
      ]
    };
    renderAnalysisPage([pendingResult, refreshedResult]);

    const highSegment = await screen.findByTestId("timeline-segment-high-silence");
    await user.click(highSegment);
    await user.selectOptions(getSeveritySelect(), "HIGH");

    expect(await screen.findByTestId("timeline-segment-high-silence")).toHaveClass("selected");

    await waitFor(
      () => expect(screen.queryByTestId("timeline-segment-high-silence")).not.toBeInTheDocument(),
      { timeout: 3000 }
    );

    await user.selectOptions(getSeveritySelect(), "ALL");

    const restoredSegment = await screen.findByTestId("timeline-segment-high-silence");
    expect(restoredSegment).not.toHaveClass("selected");
  });
});
