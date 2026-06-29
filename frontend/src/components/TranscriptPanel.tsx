import { Clipboard } from "lucide-react";
import { useMemo, useState } from "react";
import type { TranscriptResult, TranscriptSegment } from "../types/analysis";
import { formatTime } from "../utils/time";

interface TranscriptPanelProps {
  transcript: TranscriptResult | null;
  onSeek: (segment: TranscriptSegment) => void;
}

export function TranscriptPanel({ transcript, onSeek }: TranscriptPanelProps) {
  const [query, setQuery] = useState("");
  const segments = useMemo(() => transcript?.segments ?? [], [transcript]);
  const filtered = useMemo(() => {
    const lower = query.trim().toLowerCase();
    if (!lower) return segments;
    return segments.filter((segment) => segment.text.toLowerCase().includes(lower));
  }, [query, segments]);

  if (transcript?.error) {
    return <p className="warning-copy">{transcript.error}</p>;
  }

  if (segments.length === 0) {
    return <p className="empty-copy">Transcript 결과가 없습니다.</p>;
  }

  async function copyTranscript() {
    const text = segments.map((segment) => `[${formatTime(segment.start)}] ${segment.text}`).join("\n");
    await navigator.clipboard?.writeText(text);
  }

  return (
    <div className="transcript-panel">
      <div className="transcript-tools">
        <input
          type="search"
          placeholder="Transcript 검색"
          value={query}
          onChange={(event) => setQuery(event.currentTarget.value)}
        />
        <button type="button" className="secondary-button" onClick={copyTranscript}>
          <Clipboard aria-hidden="true" />
          복사
        </button>
      </div>
      <div className="transcript-list">
        {filtered.map((segment) => (
          <button key={segment.id} type="button" onClick={() => onSeek(segment)}>
            <span>{formatTime(segment.start)} - {formatTime(segment.end)}</span>
            <strong>{segment.text}</strong>
          </button>
        ))}
      </div>
    </div>
  );
}
