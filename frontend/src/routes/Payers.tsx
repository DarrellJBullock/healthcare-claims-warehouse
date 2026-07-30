import { PayerPerformanceCard } from "../components/payers/PayerPerformanceCard";
import { PayerRankingTable, type PayerPerformanceRow } from "../components/payers/PayerRankingTable";
import { ErrorState } from "../components/ui/EmptyState";
import { SkeletonGrid, SkeletonTable } from "../components/ui/Skeleton";
import { useAnalytics } from "../hooks/useAnalytics";
import { api } from "../lib/api";

export function Payers() {
  const { data, loading, error, refetch } = useAnalytics<PayerPerformanceRow[]>((role) =>
    api.payerPerformance(role) as Promise<PayerPerformanceRow[]>
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">Payer Performance</h1>
        <p className="text-sm text-slate-500">Ranked by total paid amount, with days-to-pay and adjustment trends.</p>
      </div>

      {loading && (
        <>
          <SkeletonGrid />
          <SkeletonTable />
        </>
      )}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {!loading && !error && data && (
        <>
          <PayerPerformanceCard rows={data} />
          <PayerRankingTable rows={data} />
        </>
      )}
    </div>
  );
}
