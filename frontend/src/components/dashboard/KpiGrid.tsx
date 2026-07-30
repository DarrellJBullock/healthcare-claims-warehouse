import { MetricCard } from "../ui/MetricCard";
import { formatCurrency, formatPercent } from "../../lib/formatters";

export interface DashboardSummary {
  total_claims: number;
  total_billed: number;
  total_paid: number;
  avg_paid_amount: number;
  denial_rate: number;
  top_denial_reason: string | null;
  open_data_quality_issues: number;
}

export function KpiGrid({ summary }: { summary: DashboardSummary }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard label="Total Claims" value={summary.total_claims.toLocaleString()} hint="all time" />
      <MetricCard label="Total Billed" value={formatCurrency(summary.total_billed)} />
      <MetricCard label="Total Paid" value={formatCurrency(summary.total_paid)} hint={`avg ${formatCurrency(summary.avg_paid_amount)}`} />
      <MetricCard
        label="Denial Rate"
        value={formatPercent(summary.denial_rate)}
        hint={summary.top_denial_reason ?? undefined}
        trend={{ direction: summary.denial_rate > 0.15 ? "up" : "down", label: summary.denial_rate > 0.15 ? "elevated" : "healthy" }}
      />
    </div>
  );
}
