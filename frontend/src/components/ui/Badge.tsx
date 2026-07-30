import type { BadgeTone } from "../../lib/badgeTones";

export function Badge({ tone = "neutral", children }: { tone?: BadgeTone; children: React.ReactNode }) {
  const TONE_CLASSES: Record<BadgeTone, string> = {
    neutral: "bg-surface-700 text-slate-300 border-surface-600",
    success: "bg-risk-low/10 text-risk-low border-risk-low/30",
    warning: "bg-risk-medium/10 text-risk-medium border-risk-medium/30",
    danger: "bg-risk-critical/10 text-risk-critical border-risk-critical/30",
    info: "bg-accent-500/10 text-accent-400 border-accent-500/30",
  };

  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium ${TONE_CLASSES[tone]}`}>
      {children}
    </span>
  );
}
