import { Card } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";
import { formatDateTime } from "../../lib/formatters";

export interface AuditEventSummary {
  event_timestamp: string;
  user_role: string;
  action: string;
  resource_type: string;
  status: string;
}

export function RecentAuditEvents({ events }: { events: AuditEventSummary[] }) {
  return (
    <Card title="Recent Audit Events">
      {events.length === 0 ? (
        <EmptyState title="No audit events visible" description="This role does not have access to the audit log, or nothing has happened yet." />
      ) : (
        <ul className="flex flex-col divide-y divide-surface-700/50">
          {events.map((event, idx) => (
            <li key={idx} className="flex items-center justify-between gap-3 py-2.5 text-xs">
              <div className="flex flex-col">
                <span className="font-medium text-slate-200">{event.action.replaceAll("_", " ")}</span>
                <span className="text-slate-500">
                  {event.user_role} · {event.resource_type || "—"}
                </span>
              </div>
              <span className="whitespace-nowrap text-slate-500">{formatDateTime(event.event_timestamp)}</span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
