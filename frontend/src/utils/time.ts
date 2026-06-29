export function formatTime(seconds: number): string {
  const safe = Math.max(0, seconds);
  const minutes = Math.floor(safe / 60);
  const remaining = safe - minutes * 60;
  return `${minutes.toString().padStart(2, "0")}:${remaining.toFixed(2).padStart(5, "0")}`;
}

