import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { VideoUploader } from "../components/VideoUploader";

describe("VideoUploader", () => {
  it("disables submit when no file is selected", () => {
    render(<VideoUploader onSubmit={vi.fn()} />);
    expect(screen.getByRole("button", { name: "분석 시작" })).toBeDisabled();
  });

  it("shows selected MP4 filename", async () => {
    const user = userEvent.setup();
    render(<VideoUploader onSubmit={vi.fn()} />);
    const file = new File(["video"], "sample.mp4", { type: "video/mp4" });
    await user.upload(screen.getByLabelText(/MP4 영상을/), file);
    expect(screen.getByText("sample.mp4")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "분석 시작" })).toBeEnabled();
  });

  it("shows invalid extension error", async () => {
    render(<VideoUploader onSubmit={vi.fn()} />);
    const file = new File(["text"], "sample.mov", { type: "video/quicktime" });
    fireEvent.change(screen.getByLabelText(/MP4 영상을/), { target: { files: [file] } });
    expect(screen.getByText("MP4 파일만 업로드할 수 있습니다.")).toBeInTheDocument();
  });
});
