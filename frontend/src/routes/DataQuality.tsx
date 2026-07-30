import { useState } from "react";

import { FailedRecordsPreview } from "../components/data-quality/FailedRecordsPreview";
import { QualityChecksTable, type DataQualityResultRow } from "../components/data-quality/QualityChecksTable";
import { QualityScoreCard, type QualityScorecardRow } from "../components/data-quality/QualityScoreCard";
import { Button } from "../components/ui/Button";
import { ErrorState } from "../components/ui/EmptyState";
import { SkeletonGrid, SkeletonTable } from "../components/ui/Skeleton";
import { useAnalytics } from "../hooks/useAnalytics";
import { useRole } from "../hooks/useRole";
import { api, ApiError } from "../lib/api";
import { getPermissions } from "../lib/roles";

interface DataQualityResponse {
  scorecard: QualityScorecardRow[];
  results: DataQualityResultRow[];
}

export function DataQuality() {
  const { role } = useRole();
  const permissions = getPermissions(role);
  const [running, setRunning] = useState(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);

  const { data, loading, error, refetch } = useAnalytics<DataQualityResponse>((r) =>
    api.dataQualityResults(r) as Promise<DataQualityResponse>
  );

  const handleRun = async () => {
    setRunning(true);
    setRunMessage(null);
    try {
      const summary = (await api.runDataQualityChecks(role)) as { total_checks: number; passed_checks: number; failed_checks: number };
      setRunMessage(`Ran ${summary.total_checks} checks — ${summary.passed_checks} passed, ${summary.failed_checks} failed.`);
      refetch();
    } catch (err) {
      setRunMessage(err instanceof ApiError ? err.message : "Failed to run checks.");
    } finally {
      setRunning(false);
    }
  };

  if (!permissions.canViewDataQuality) {
    return <ErrorState message="This role does not have access to the Data Quality Center. Switch to Admin or Data Engineer." />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold text-slate-100">Data Quality Center</h1>
          <p className="text-sm text-slate-500">Pipeline health, quality scores, and failing checks.</p>
        </div>
        {permissions.canRunQualityChecks && (
          <div className="flex items-center gap-3">
            <Button onClick={handleRun} disabled={running}>
              {running ? "Running…" : "Run Quality Checks"}
            </Button>
            {runMessage && <span className="text-xs text-slate-400">{runMessage}</span>}
          </div>
        )}
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
          <QualityScoreCard rows={data.scorecard} />
          <QualityChecksTable rows={data.results} />
          <FailedRecordsPreview rows={data.results} />
        </>
      )}
    </div>
  );
}
