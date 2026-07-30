import { Card } from "../ui/Card";
import { formatPercent } from "../../lib/formatters";

export function DenialSummary({ denialRate, topReason }: { denialRate: number; topReason: string | null }) {
  return (
    <Card title="Denial Summary">
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">Overall denial rate</span>
          <span className="text-lg font-semibold text-slate-100">{formatPercent(denialRate)}</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-surface-700">
          <div
            className={`h-full rounded-full ${denialRate > 0.2 ? "bg-risk-critical" : denialRate > 0.1 ? "bg-risk-medium" : "bg-risk-low"}`}
            style={{ width: `${Math.min(denialRate * 100, 100)}%` }}
          />
        </div>
        <div className="flex items-center justify-between border-t border-surface-700/60 pt-3 text-xs">
          <span className="text-slate-400">Top denial reason</span>
          <span className="font-medium text-slate-200">{topReason ?? "None recorded"}</span>
        </div>
      </div>
    </Card>
  );
}
