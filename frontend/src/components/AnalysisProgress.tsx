import type { AnalysisStatus } from "../types/analysis";

const steps: Array<{ status: AnalysisStatus; label: string }> = [
  { status: "VALIDATING", label: "파일 확인" },
  { status: "EXTRACTING_METADATA", label: "메타데이터 추출" },
  { status: "DETECTING_SILENCE", label: "오디오 분석" },
  { status: "TRANSCRIBING", label: "음성 transcript 생성" },
  { status: "DETECTING_SCENES", label: "장면 전환 분석" },
  { status: "BUILDING_REPORT", label: "보고서 생성" }
];

interface AnalysisProgressProps {
  currentStep: AnalysisStatus | null;
}

export function AnalysisProgress({ currentStep }: AnalysisProgressProps) {
  const activeIndex = steps.findIndex((step) => step.status === currentStep);
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>분석 진행</h2>
        <p>Whisper transcript 생성은 CPU 환경에서 시간이 걸릴 수 있습니다.</p>
      </div>
      <ol className="progress-list">
        {steps.map((step, index) => (
          <li
            key={step.status}
            className={index < activeIndex ? "done" : index === activeIndex ? "active" : ""}
          >
            <span>{index + 1}</span>
            {step.label}
          </li>
        ))}
      </ol>
    </section>
  );
}

