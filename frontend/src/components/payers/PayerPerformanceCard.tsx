import { MetricCard } from "../ui/MetricCard";
import { formatCurrency, formatNumber } from "../../lib/formatters";
import type { PayerPerformanceRow } from "./PayerRankingTable";

export function PayerPerformanceCard({ rows }: { rows: PayerPerformanceRow[] }) {
  const totalPaid = rows.reduce((sum, r) => sum + r.total_paid, 0);
  const daysToPayValues = rows.filter((r) => r.avg_days_to_pay != null).map((r) => r.avg_days_to_pay as number);
  const avgDaysToPay = daysToPayValues.length ? daysToPayValues.reduce((a, b) => a + b, 0) / daysToPayValues.length : null;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard label="Payers Tracked" value={formatNumber(rows.length)} />
      <MetricCard label="Total Paid" value={formatCurrency(totalPaid)} />
      <MetricCard label="Avg Days to Pay" value={avgDaysToPay != null ? avgDaysToPay.toFixed(1) : "—"} />
      <MetricCard label="Total Adjustments" value={formatCurrency(rows.reduce((sum, r) => sum + r.total_adjustments, 0))} />
    </div>
  );
}
