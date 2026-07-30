import { Card } from "../components/ui/Card";
import { ErrorState } from "../components/ui/EmptyState";
import { SkeletonTable } from "../components/ui/Skeleton";
import { MemberUtilizationTable, type MemberUtilizationRow } from "../components/members/MemberUtilizationTable";
import { Table } from "../components/ui/Table";
import { formatCurrency, formatNumber } from "../lib/formatters";
import { useAnalytics } from "../hooks/useAnalytics";
import { api } from "../lib/api";

interface AggregateRow {
  plan_type: string;
  member_count: number;
  total_claims: number;
  total_paid: number;
  high_cost_members: number;
}

type MemberUtilizationResponse =
  | { aggregate_only: true; results: AggregateRow[] }
  | { aggregate_only: false; results: MemberUtilizationRow[] };

export function Members() {
  const { data, loading, error, refetch } = useAnalytics<MemberUtilizationResponse>((role) =>
    api.memberUtilization(role) as Promise<MemberUtilizationResponse>
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">Member Utilization</h1>
        <p className="text-sm text-slate-500">
          Keyed by surrogate analytics key only — no raw member IDs or PHI ever leave the warehouse layer.
        </p>
      </div>

      {loading && <SkeletonTable />}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {!loading && !error && data && data.aggregate_only && (
        <Card title="Utilization by Plan Type (Aggregate Only — no per-member detail for this role)">
          <Table
            keyField={(row: AggregateRow) => row.plan_type}
            columns={[
              { header: "Plan Type", render: (row) => row.plan_type },
              { header: "Members", render: (row) => formatNumber(row.member_count), align: "right" },
              { header: "Claims", render: (row) => formatNumber(row.total_claims), align: "right" },
              { header: "Total Paid", render: (row) => formatCurrency(row.total_paid), align: "right" },
              { header: "High-Cost Members", render: (row) => row.high_cost_members, align: "right" },
            ]}
            rows={data.results}
          />
        </Card>
      )}

      {!loading && !error && data && !data.aggregate_only && <MemberUtilizationTable rows={data.results} />}
    </div>
  );
}
