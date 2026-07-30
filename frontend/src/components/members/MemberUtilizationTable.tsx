import { Table } from "../ui/Table";
import { formatCurrency, formatNumber } from "../../lib/formatters";
import { MemberRiskBadge } from "./MemberRiskBadge";

export interface MemberUtilizationRow {
  analytics_member_key: number;
  plan_type: string;
  gender: string;
  birth_year: number;
  claim_count: number;
  total_billed: number;
  total_paid: number;
  cost_percentile: number;
  is_high_cost: boolean;
  coverage_status: string | null;
}

export function MemberUtilizationTable({ rows }: { rows: MemberUtilizationRow[] }) {
  return (
    <Table
      keyField={(row) => row.analytics_member_key}
      columns={[
        { header: "Member Key", render: (row) => `#${row.analytics_member_key}` },
        { header: "Plan", render: (row) => row.plan_type },
        { header: "Birth Year", render: (row) => row.birth_year },
        { header: "Claims", render: (row) => formatNumber(row.claim_count), align: "right" },
        { header: "Total Paid", render: (row) => formatCurrency(row.total_paid), align: "right" },
        { header: "Cost Percentile", render: (row) => `P${row.cost_percentile}`, align: "right" },
        { header: "Coverage", render: (row) => row.coverage_status ?? "—" },
        { header: "Risk", render: (row) => <MemberRiskBadge isHighCost={row.is_high_cost} /> },
      ]}
      rows={rows}
    />
  );
}
