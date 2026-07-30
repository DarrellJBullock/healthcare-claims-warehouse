import { MetricCard } from "../ui/MetricCard";
import { formatCurrency, formatNumber, formatPercent } from "../../lib/formatters";
import type { ProviderPerformanceRow } from "./ProviderRankingTable";

export function ProviderPerformanceCard({ rows }: { rows: ProviderPerformanceRow[] }) {
  const totalPaid = rows.reduce((sum, r) => sum + r.total_paid, 0);
  const totalClaims = rows.reduce((sum, r) => sum + r.total_claims, 0);
  const avgDenialRate = rows.length ? rows.reduce((sum, r) => sum + r.denial_rate, 0) / rows.length : 0;
  const highRiskCount = rows.filter((r) => r.is_high_risk).length;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard label="Providers Tracked" value={formatNumber(rows.length)} />
      <MetricCard label="Total Paid" value={formatCurrency(totalPaid)} hint={`${formatNumber(totalClaims)} claims`} />
      <MetricCard label="Avg Denial Rate" value={formatPercent(avgDenialRate)} />
      <MetricCard label="High-Risk Providers" value={formatNumber(highRiskCount)} hint="denial rate > 25%" />
    </div>
  );
}
