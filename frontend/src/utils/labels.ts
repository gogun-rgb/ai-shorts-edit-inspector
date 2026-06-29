import type { Severity } from "../types/analysis";

export const severityLabel: Record<Severity, string> = {
  INFO: "정보",
  LOW: "낮음",
  MEDIUM: "보통",
  HIGH: "높음"
};

export const findingTypeLabel: Record<string, string> = {
  SILENCE: "무음",
  START_SILENCE: "시작 무음",
  END_SILENCE: "끝 무음",
  LONG_SCENE: "긴 장면",
  VERY_LONG_SCENE: "매우 긴 장면",
  SHORT_SCENE: "짧은 컷",
  RAPID_CUTS: "빠른 컷 확인 필요",
  SUBTITLE_GAP: "자막 공백",
  ASPECT_RATIO: "화면 비율",
  VIDEO_DURATION: "영상 길이",
  MISSING_AUDIO: "오디오 없음",
  TRANSCRIPTION_ERROR: "Transcript 오류"
};

export const severityOrder = ["HIGH", "MEDIUM", "LOW", "INFO"] as const;

export const findingTypeOrder = [
  "START_SILENCE",
  "END_SILENCE",
  "SILENCE",
  "LONG_SCENE",
  "VERY_LONG_SCENE",
  "SHORT_SCENE",
  "RAPID_CUTS",
  "SUBTITLE_GAP",
  "ASPECT_RATIO",
  "VIDEO_DURATION",
  "MISSING_AUDIO",
  "TRANSCRIPTION_ERROR"
] as const;
