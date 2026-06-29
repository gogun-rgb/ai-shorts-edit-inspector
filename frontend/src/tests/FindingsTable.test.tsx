import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { FindingsTable } from "../components/FindingsTable";
import type { Finding } from "../types/analysis";

const finding: Finding = {
  id: "finding-1",
  type: "SILENCE",
  severity: "HIGH",
  start: 3.2,
  end: 5.1,
  duration: 1.9,
  title: "긴 무음 구간",
  reason: "1.9초 동안 음량이 기준 이하였습니다.",
  suggestion: "무음 제거를 검토하세요.",
  source: "test",
  metadata: {}
};

describe("FindingsTable", () => {
  it("renders findings and severity text", () => {
    render(<FindingsTable findings={[finding]} onSeek={vi.fn()} />);
    expect(screen.getByText("무음")).toBeInTheDocument();
    expect(screen.getByText("높음")).toBeInTheDocument();
  });

  it("calls seek when a row is clicked", async () => {
    const user = userEvent.setup();
    const onSeek = vi.fn();
    render(<FindingsTable findings={[finding]} onSeek={onSeek} />);
    await user.click(screen.getByText("1.9초 동안 음량이 기준 이하였습니다."));
    expect(onSeek).toHaveBeenCalledWith(finding);
  });
});

