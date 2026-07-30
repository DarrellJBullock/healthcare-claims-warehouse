import { useState } from "react";

import { ClaimDetailDrawer } from "../components/claims/ClaimDetailDrawer";
import { ClaimsTable, type ClaimListItem } from "../components/claims/ClaimsTable";
import { Button } from "../components/ui/Button";
import { ErrorState } from "../components/ui/EmptyState";
import { FilterBar, FilterField, filterInputClass } from "../components/ui/FilterBar";
import { SkeletonTable } from "../components/ui/Skeleton";
import { useAnalytics } from "../hooks/useAnalytics";
import { useRole } from "../hooks/useRole";
import { api } from "../lib/api";
import { getPermissions } from "../lib/roles";

interface ClaimsResponse {
  count: number;
  page: number;
  page_size: number;
  results: ClaimListItem[];
}

const STATUS_OPTIONS = ["Paid", "Denied", "Pending", "Partially Paid"];

export function Claims() {
  const { role } = useRole();
  const permissions = getPermissions(role);
  const [filters, setFilters] = useState({ date_from: "", date_to: "", status: "" });
  const [page, setPage] = useState(1);
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null);

  const { data, loading, error, refetch } = useAnalytics<ClaimsResponse>((r) => {
    const params: Record<string, string> = { page: String(page), page_size: "25" };
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;
    if (filters.status) params.status = filters.status;
    return api.claims(r, params) as Promise<ClaimsResponse>;
  }, [page]);

  if (!permissions.canViewRowLevelClaims) {
    return (
      <ErrorState message="This role does not have access to row-level claims. Switch to Admin, Data Engineer, or Claims Analyst." />
    );
  }

  const totalPages = data ? Math.max(Math.ceil(data.count / data.page_size), 1) : 1;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">Claims</h1>
        <p className="text-sm text-slate-500">Row-level claims with masked identifiers by default.</p>
      </div>

      <FilterBar>
        <FilterField label="Date From">
          <input
            type="date"
            className={filterInputClass}
            value={filters.date_from}
            onChange={(e) => setFilters((f) => ({ ...f, date_from: e.target.value }))}
          />
        </FilterField>
        <FilterField label="Date To">
          <input
            type="date"
            className={filterInputClass}
            value={filters.date_to}
            onChange={(e) => setFilters((f) => ({ ...f, date_to: e.target.value }))}
          />
        </FilterField>
        <FilterField label="Status">
          <select
            className={filterInputClass}
            value={filters.status}
            onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
          >
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </FilterField>
        <Button
          type="button"
          variant="secondary"
          onClick={() => {
            setPage(1);
            refetch();
          }}
        >
          Apply Filters
        </Button>
      </FilterBar>

      {loading && <SkeletonTable />}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {!loading && !error && data && (
        <>
          <ClaimsTable claims={data.results} onSelect={setSelectedClaimId} />
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>
              Page {data.page} of {totalPages} — {data.count.toLocaleString()} claims
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

      {selectedClaimId && <ClaimDetailDrawer claimId={selectedClaimId} onClose={() => setSelectedClaimId(null)} />}
    </div>
  );
}
