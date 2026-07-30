import { Badge } from "../ui/Badge";

export function MemberRiskBadge({ isHighCost }: { isHighCost: boolean }) {
  return isHighCost ? <Badge tone="danger">High Cost</Badge> : <Badge tone="success">Normal</Badge>;
}
