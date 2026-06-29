interface ErrorStateProps {
  message: string;
}

export function ErrorState({ message }: ErrorStateProps) {
  return (
    <section className="panel error-panel">
      <h2>분석을 완료하지 못했습니다</h2>
      <p>{message}</p>
    </section>
  );
}

