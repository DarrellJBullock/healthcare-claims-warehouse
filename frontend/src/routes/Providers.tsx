import { ProviderPerformanceCard } from "../components/providers/ProviderPerformanceCard";
import { ProviderRankingTable, type ProviderPerformanceRow } from "../components/providers/ProviderRankingTable";
import { ErrorState } from "../components/ui/EmptyState";
import { SkeletonGrid, SkeletonTable } from "../components/ui/Skeleton";
import { useAnalytics } from "../hooks/useAnalytics";
import { api } from "../lib/api";

export function Providers() {
  const { data, loading, error, refetch } = useAnalytics<ProviderPerformanceRow[]>((role) =>
    api.providerPerformance(role) as Promise<ProviderPerformanceRow[]>
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">Provider Performance</h1>
        <p className="text-sm text-slate-500">Ranked by total paid amount, with denial rate and risk flags.</p>
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
          <ProviderPerformanceCard rows={data} />
          <ProviderRankingTable rows={data} />
        </>
      )}
    </div>
  );
}
