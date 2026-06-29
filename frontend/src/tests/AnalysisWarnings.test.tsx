import { MemoryRouter, Route, Routes } from "react-router-dom";
import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AnalysisPage } from "../pages/AnalysisPage";
import type { AnalysisResult } from "../types/analysis";

const transcriptWarning = "Whisper transcript 생성에 실패했습니다.";

const result: AnalysisResult = {
  analysisId: "123",
  status: "PARTIAL_SUCCESS",
  createdAt: new Date().toISOString(),
  completedAt: new Date().toISOString(),
  currentStep: "PARTIAL_SUCCESS",
  metadata: {
    fileName: "source.mp4",
    fileSizeBytes: 100,
    duration: 10,
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
    readinessScore: 88,
    grade: "Minor fixes",
    totalFindings: 0,
    highCount: 0,
    mediumCount: 0,
    lowCount: 0,
    infoCount: 0
  },
  findings: [],
  transcript: {
    language: "ko",
    languageProbability: 0.9,
    duration: 10,
    segments: [],
    error: transcriptWarning
  },
  scenes: [{ index: 0, start: 0, end: 10, duration: 10 }],
  warnings: [transcriptWarning],
  error: null
};

describe("AnalysisPage warnings", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows partial success warnings", async () => {
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

    await waitFor(() => expect(screen.getByText("부분 성공")).toBeInTheDocument());
    expect(screen.getAllByText(transcriptWarning).length).toBeGreaterThan(0);
  });
});
