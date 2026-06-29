export function SettingsPanel() {
  return (
    <aside className="note-panel">
      <h2>분석 기준</h2>
      <ul>
        <li>무음: -35dB 이하 0.8초 이상</li>
        <li>긴 장면: 6초 이상, 매우 긴 장면은 10초 이상</li>
        <li>빠른 컷: 3초 안에 짧은 컷 4개 이상</li>
        <li>자막 공백: 업로드한 SRT/VTT와 transcript 타임스탬프 비교</li>
      </ul>
    </aside>
  );
}

