import { AuditLogTable, type AuditLogRow } from "../components/audit/AuditLogTable";
import { ErrorState } from "../components/ui/EmptyState";
import { SkeletonTable } from "../components/ui/Skeleton";
import { useAnalytics } from "../hooks/useAnalytics";
import { useRole } from "../hooks/useRole";
import { api } from "../lib/api";
import { getPermissions } from "../lib/roles";

interface AuditLogResponse {
  count: number;
  results: AuditLogRow[];
}

export function AuditLog() {
  const { role } = useRole();
  const permissions = getPermissions(role);

  const { data, loading, error, refetch } = useAnalytics<AuditLogResponse>((r) =>
    api.auditLog(r) as Promise<AuditLogResponse>
  );

  if (!permissions.canViewAuditLog) {
    return <ErrorState message="This role does not have access to the audit log. Switch to Admin or Auditor." />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">Audit Log</h1>
        <p className="text-sm text-slate-500">Every sensitive action across the warehouse, in order.</p>
      </div>

      {loading && <SkeletonTable />}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {!loading && !error && data && <AuditLogTable rows={data.results} />}
    </div>
  );
}
