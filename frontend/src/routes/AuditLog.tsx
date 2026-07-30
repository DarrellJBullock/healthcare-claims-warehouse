import { useState } from "react";

import { AuditLogTable, type AuditLogRow } from "../components/audit/AuditLogTable";
import { Button } from "../components/ui/Button";
import { ErrorState } from "../components/ui/EmptyState";
import { SkeletonTable } from "../components/ui/Skeleton";
import { useAnalytics } from "../hooks/useAnalytics";
import { useRole } from "../hooks/useRole";
import { api } from "../lib/api";
import { getPermissions } from "../lib/roles";

const PAGE_SIZE = 25;

interface AuditLogResponse {
  count: number;
  results: AuditLogRow[];
}

export function AuditLog() {
  const { role } = useRole();
  const permissions = getPermissions(role);
  const [page, setPage] = useState(1);

  const { data, loading, error, refetch } = useAnalytics<AuditLogResponse>(
    (r) => api.auditLog(r, { page: String(page), page_size: String(PAGE_SIZE) }) as Promise<AuditLogResponse>,
    [page]
  );

  if (!permissions.canViewAuditLog) {
    return <ErrorState message="This role does not have access to the audit log. Switch to Admin or Auditor." />;
  }

  const totalPages = data ? Math.max(Math.ceil(data.count / PAGE_SIZE), 1) : 1;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">Audit Log</h1>
        <p className="text-sm text-slate-500">Every sensitive action across the warehouse, in order.</p>
      </div>

      {loading && <SkeletonTable />}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {!loading && !error && data && (
        <>
          <AuditLogTable rows={data.results} />
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>
              Page {page} of {totalPages} — {data.count.toLocaleString()} events
            </span>
            <div className="flex gap-2">
              <Button variant="secondary" disabled={page <= 1} onClick={() => setPage((p) => Math.max(p - 1, 1))}>
                Previous
              </Button>
              <Button variant="secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
