import { Card } from "../ui/Card";
import { formatDateTime } from "../../lib/formatters";

export interface QualityScorecardRow {
  table_name: string;
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  quality_score: number;
  last_run_at: string | null;
}

export function QualityScoreCard({ rows }: { rows: QualityScorecardRow[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {rows.map((row) => (
        <Card key={row.table_name} title={row.table_name}>
          <div className="flex items-end justify-between">
            <span
              className={`text-3xl font-semibold ${
                row.quality_score >= 90 ? "text-risk-low" : row.quality_score >= 70 ? "text-risk-medium" : "text-risk-critical"
              }`}
            >
              {row.quality_score.toFixed(0)}%
            </span>
            <span className="text-xs text-slate-500">
              {row.passed_checks}/{row.total_checks} passed
            </span>
          </div>
          <p className="mt-2 text-[11px] text-slate-500">Last run {formatDateTime(row.last_run_at)}</p>
        </Card>
      ))}
    </div>
  );
}
