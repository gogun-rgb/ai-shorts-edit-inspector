export type AnalysisStatus =
  | "QUEUED"
  | "VALIDATING"
  | "EXTRACTING_METADATA"
  | "DETECTING_SILENCE"
  | "TRANSCRIBING"
  | "DETECTING_SCENES"
  | "BUILDING_REPORT"
  | "COMPLETED"
  | "PARTIAL_SUCCESS"
  | "FAILED";

export type Severity = "INFO" | "LOW" | "MEDIUM" | "HIGH";

export interface VideoMetadata {
  fileName: string;
  fileSizeBytes: number;
  duration: number;
  width: number;
  height: number;
  aspectRatio: number;
  fps: number | null;
  videoCodec: string | null;
  audioCodec: string | null;
  hasAudio: boolean;
  averageBitrate: number | null;
}

export interface Finding {
  id: string;
  type: string;
  severity: Severity;
  start: number;
  end: number;
  duration: number;
  title: string;
  reason: string;
  suggestion: string;
  source: string;
  metadata: Record<string, unknown>;
}

export interface TranscriptSegment {
  id: number;
  start: number;
  end: number;
  text: string;
  words: Array<{ start: number; end: number; word: string }>;
}

export interface TranscriptResult {
  language: string | null;
  languageProbability: number | null;
  duration: number | null;
  segments: TranscriptSegment[];
  error: string | null;
}

export interface Scene {
  index: number;
  start: number;
  end: number;
  duration: number;
}

export interface Summary {
  readinessScore: number;
  grade: string;
  totalFindings: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  infoCount: number;
}

export interface AnalysisResult {
  analysisId: string;
  status: AnalysisStatus;
  createdAt: string;
  completedAt: string | null;
  currentStep: AnalysisStatus | null;
  metadata: VideoMetadata | null;
  summary: Summary | null;
  findings: Finding[];
  transcript: TranscriptResult | null;
  scenes: Scene[];
  warnings: string[];
  error: string | null;
}

