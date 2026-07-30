import { claimStatusTone } from "../../lib/badgeTones";
import { Badge } from "../ui/Badge";

export function ClaimStatusBadge({ status }: { status: string }) {
  return <Badge tone={claimStatusTone(status)}>{status}</Badge>;
}
