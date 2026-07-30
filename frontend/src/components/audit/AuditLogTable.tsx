import { Table } from "../ui/Table";
import { formatDateTime } from "../../lib/formatters";
import { AuditEventBadge } from "./AuditEventBadge";

export interface AuditLogRow {
  id: number;
  event_timestamp: string;
  user_id: string;
  user_role: string;
  action: string;
  resource_type: string;
  resource_id: string;
  reason: string;
  status: string;
}

export function AuditLogTable({ rows }: { rows: AuditLogRow[] }) {
  return (
    <Table
      keyField={(row) => row.id}
      columns={[
        { header: "Timestamp", render: (row) => formatDateTime(row.event_timestamp) },
        { header: "User", render: (row) => row.user_id },
        { header: "Role", render: (row) => row.user_role },
        { header: "Action", render: (row) => row.action.replaceAll("_", " ") },
        { header: "Resource", render: (row) => `${row.resource_type || "—"} ${row.resource_id ? `#${row.resource_id}` : ""}` },
        { header: "Reason", render: (row) => <span className="text-slate-400">{row.reason || "—"}</span> },
        { header: "Status", render: (row) => <AuditEventBadge status={row.status} /> },
      ]}
      rows={rows}
    />
  );
}
