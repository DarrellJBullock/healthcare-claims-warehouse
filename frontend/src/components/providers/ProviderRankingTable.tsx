import { Badge } from "../ui/Badge";
import { Table } from "../ui/Table";
import { formatCurrency, formatPercent } from "../../lib/formatters";

export interface ProviderPerformanceRow {
  analytics_provider_key: number;
  provider_name: string;
  specialty: string;
  network_status: string;
  total_claims: number;
  total_billed: number;
  total_paid: number;
  denial_rate: number;
  avg_reimbursement: number;
  top_procedure_category: string | null;
  paid_rank: number;
  is_high_risk: boolean;
}

export function ProviderRankingTable({ rows }: { rows: ProviderPerformanceRow[] }) {
  return (
    <Table
      keyField={(row) => row.analytics_provider_key}
      columns={[
        { header: "Rank", render: (row) => `#${row.paid_rank}` },
        { header: "Provider", render: (row) => row.provider_name },
        { header: "Specialty", render: (row) => row.specialty },
        { header: "Network", render: (row) => <Badge tone={row.network_status === "In-Network" ? "success" : "warning"}>{row.network_status}</Badge> },
        { header: "Claims", render: (row) => row.total_claims, align: "right" },
        { header: "Paid", render: (row) => formatCurrency(row.total_paid), align: "right" },
        { header: "Denial Rate", render: (row) => formatPercent(row.denial_rate), align: "right" },
        { header: "Avg Reimb.", render: (row) => formatCurrency(row.avg_reimbursement), align: "right" },
        { header: "Top Procedure", render: (row) => row.top_procedure_category ?? "—" },
        { header: "Risk", render: (row) => (row.is_high_risk ? <Badge tone="danger">High Risk</Badge> : <Badge tone="success">Normal</Badge>) },
      ]}
      rows={rows}
    />
  );
}
