import type { AnalysisResult } from "../types/analysis";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

interface CreateAnalysisPayload {
  video: File;
  subtitle?: File | null;
  language?: string;
  silenceThresholdDb?: number;
  minSilenceDuration?: number;
  longSceneSeconds?: number;
}

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail ?? "요청 처리 중 오류가 발생했습니다.";
  } catch {
    return "요청 처리 중 오류가 발생했습니다.";
  }
}

export async function createAnalysis(payload: CreateAnalysisPayload): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("video", payload.video);
  if (payload.subtitle) form.append("subtitle", payload.subtitle);
  if (payload.language) form.append("language", payload.language);
  if (payload.silenceThresholdDb !== undefined) form.append("silenceThresholdDb", String(payload.silenceThresholdDb));
  if (payload.minSilenceDuration !== undefined) form.append("minSilenceDuration", String(payload.minSilenceDuration));
  if (payload.longSceneSeconds !== undefined) form.append("longSceneSeconds", String(payload.longSceneSeconds));

  const response = await fetch(`${API_BASE}/api/analyses`, {
    method: "POST",
    body: form
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<AnalysisResult>;
}

export async function fetchAnalysis(analysisId: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE}/api/analyses/${analysisId}`);
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<AnalysisResult>;
}

export async function deleteAnalysis(analysisId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/analyses/${analysisId}`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
}

export function videoUrl(analysisId: string): string {
  return `${API_BASE}/api/analyses/${analysisId}/video`;
}

export function exportUrl(analysisId: string, format: "json" | "csv"): string {
  return `${API_BASE}/api/analyses/${analysisId}/export/${format}`;
}

