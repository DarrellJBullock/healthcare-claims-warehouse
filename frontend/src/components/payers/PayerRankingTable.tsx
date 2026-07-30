import { Badge } from "../ui/Badge";
import { Table } from "../ui/Table";
import { formatCurrency, formatPercent } from "../../lib/formatters";

export interface PayerPerformanceRow {
  analytics_payer_key: number;
  payer_name: string;
  payer_type: string;
  total_claims: number;
  total_billed: number;
  total_paid: number;
  denial_rate: number;
  avg_days_to_pay: number | null;
  total_adjustments: number;
  paid_rank: number;
}

export function PayerRankingTable({ rows }: { rows: PayerPerformanceRow[] }) {
  return (
    <Table
      keyField={(row) => row.analytics_payer_key}
      columns={[
        { header: "Rank", render: (row) => `#${row.paid_rank}` },
        { header: "Payer", render: (row) => row.payer_name },
        { header: "Type", render: (row) => <Badge tone="neutral">{row.payer_type}</Badge> },
        { header: "Claims", render: (row) => row.total_claims, align: "right" },
        { header: "Paid", render: (row) => formatCurrency(row.total_paid), align: "right" },
        { header: "Denial Rate", render: (row) => formatPercent(row.denial_rate), align: "right" },
        { header: "Avg Days to Pay", render: (row) => (row.avg_days_to_pay != null ? row.avg_days_to_pay.toFixed(1) : "—"), align: "right" },
        { header: "Adjustments", render: (row) => formatCurrency(row.total_adjustments), align: "right" },
      ]}
      rows={rows}
    />
  );
}
