import { severityTone } from "../../lib/badgeTones";
import { Badge } from "../ui/Badge";
import { Table } from "../ui/Table";
import { formatDateTime } from "../../lib/formatters";

export interface DataQualityResultRow {
  check_name: string;
  table_name: string;
  severity: string;
  status: string;
  failed_count: number;
  sample_record_key: string | null;
  message: string;
  created_at: string;
}

export function QualityChecksTable({ rows }: { rows: DataQualityResultRow[] }) {
  return (
    <Table
      keyField={(row) => `${row.check_name}-${row.created_at}`}
      columns={[
        { header: "Check", render: (row) => row.check_name },
        { header: "Table", render: (row) => row.table_name },
        { header: "Severity", render: (row) => <Badge tone={severityTone(row.severity)}>{row.severity}</Badge> },
        { header: "Status", render: (row) => <Badge tone={row.status === "PASS" ? "success" : "danger"}>{row.status}</Badge> },
        { header: "Failed Rows", render: (row) => row.failed_count, align: "right" },
        { header: "Message", render: (row) => <span className="text-slate-400">{row.message}</span> },
        { header: "Last Run", render: (row) => formatDateTime(row.created_at) },
      ]}
      rows={rows}
    />
  );
}
