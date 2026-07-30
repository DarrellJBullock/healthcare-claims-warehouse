import { Badge } from "../ui/Badge";

export function AuditEventBadge({ status }: { status: string }) {
  const tone = status === "SUCCESS" ? "success" : status === "DENIED" ? "danger" : "warning";
  return <Badge tone={tone}>{status}</Badge>;
}
