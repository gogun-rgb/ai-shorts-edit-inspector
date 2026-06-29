import { forwardRef, useImperativeHandle, useRef, useState } from "react";
import { videoUrl } from "../api/client";
import { formatTime } from "../utils/time";

export interface VideoPlayerHandle {
  seekTo: (time: number) => void;
}

interface VideoPlayerProps {
  analysisId: string;
}

export const VideoPlayer = forwardRef<VideoPlayerHandle, VideoPlayerProps>(function VideoPlayer(
  { analysisId },
  ref
) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const wrapperRef = useRef<HTMLElement | null>(null);
  const [currentTime, setCurrentTime] = useState(0);

  useImperativeHandle(ref, () => ({
    seekTo(time: number) {
      if (!videoRef.current) return;
      videoRef.current.currentTime = Math.max(0, time);
      videoRef.current.play().catch(() => undefined);
      wrapperRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }));

  return (
    <section className="player-panel" ref={wrapperRef}>
      <video
        ref={videoRef}
        controls
        preload="metadata"
        src={videoUrl(analysisId)}
        onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)}
      />
      <div className="player-meta">
        <span>현재 재생 시간</span>
        <strong>{formatTime(currentTime)}</strong>
      </div>
    </section>
  );
});

