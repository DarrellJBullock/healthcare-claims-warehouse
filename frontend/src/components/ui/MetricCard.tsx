import type { ReactNode } from "react";

export function MetricCard({
  label,
  value,
  hint,
  trend,
  icon,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  trend?: { direction: "up" | "down" | "flat"; label: string };
  icon?: ReactNode;
}) {
  const trendColor =
    trend?.direction === "up" ? "text-risk-low" : trend?.direction === "down" ? "text-risk-critical" : "text-slate-400";
  const trendGlyph = trend?.direction === "up" ? "▲" : trend?.direction === "down" ? "▼" : "▬";

  return (
    <div className="panel flex flex-col gap-2 p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">{label}</span>
        {icon && <span className="text-accent-400/80">{icon}</span>}
      </div>
      <div className="text-2xl font-semibold text-slate-50">{value}</div>
      <div className="flex items-center gap-2 text-xs text-slate-400">
        {trend && (
          <span className={`inline-flex items-center gap-1 font-medium ${trendColor}`}>
            {trendGlyph} {trend.label}
          </span>
        )}
        {hint && <span>{hint}</span>}
      </div>
    </div>
  );
}
