import type { Finding } from "../types/analysis";

export interface TimelineItem {
  finding: Finding;
  leftPercent: number;
  widthPercent: number;
  lane: number;
}

const MIN_SEGMENT_PERCENT = 1.2;

function validDuration(videoDuration: number): number {
  return Number.isFinite(videoDuration) && videoDuration > 0 ? videoDuration : 0;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function playbackPercent(currentTime: number, videoDuration: number): number {
  const duration = validDuration(videoDuration);
  if (duration === 0) return 0;
  return clamp((currentTime / duration) * 100, 0, 100);
}

export function buildTimelineItems(findings: Finding[], videoDuration: number): TimelineItem[] {
  const duration = validDuration(videoDuration);
  const sorted = [...findings].sort((left, right) => left.start - right.start || left.end - right.end);
  const laneEnds: number[] = [];

  return sorted.map((finding) => {
    const start = duration > 0 ? clamp(finding.start, 0, duration) : 0;
    const end = duration > 0 ? clamp(Math.max(finding.end, start), 0, duration) : 0;
    const rawLeft = duration > 0 ? (start / duration) * 100 : 0;
    const rawWidth = duration > 0 ? ((end - start) / duration) * 100 : 0;
    const leftPercent = clamp(rawLeft, 0, 100);
    const widthPercent = duration > 0 ? clamp(Math.max(rawWidth, MIN_SEGMENT_PERCENT), 0, 100 - leftPercent) : 0;
    const lane = laneEnds.findIndex((laneEnd) => start >= laneEnd);
    const resolvedLane = lane >= 0 ? lane : laneEnds.length;
    laneEnds[resolvedLane] = end;

    return {
      finding,
      leftPercent: Number(leftPercent.toFixed(3)),
      widthPercent: Number(widthPercent.toFixed(3)),
      lane: resolvedLane
    };
  });
}

