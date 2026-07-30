import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";

export function ComplianceChecklist({ items }: { items: { item: string; status: string }[] }) {
  return (
    <Card title="Compliance Checklist">
      {items.length === 0 ? (
        <EmptyState title="Checklist not visible for this role" description="Switch to Admin or Auditor to view the full compliance checklist." />
      ) : (
        <ul className="flex flex-col divide-y divide-surface-700/50">
          {items.map((entry) => (
            <li key={entry.item} className="flex items-center justify-between gap-3 py-2.5 text-xs">
              <span className="text-slate-300">{entry.item}</span>
              <Badge tone={entry.status === "PASS" ? "success" : "danger"}>{entry.status}</Badge>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
