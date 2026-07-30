import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";
import { formatDateTime } from "../../lib/formatters";

export function MaskingStatusCard({
  phiRiskStatus,
  lastSensitiveViewEvent,
}: {
  phiRiskStatus: string;
  lastSensitiveViewEvent: { timestamp: string; role: string; action: string } | null;
}) {
  return (
    <Card title="Masking &amp; PHI Risk Status">
      <div className="flex flex-col gap-3 text-xs">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">PHI risk status</span>
          <Badge tone="success">{phiRiskStatus}</Badge>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Last sensitive view</span>
          <span className="text-slate-200">
            {lastSensitiveViewEvent
              ? `${lastSensitiveViewEvent.action.replaceAll("_", " ")} · ${formatDateTime(lastSensitiveViewEvent.timestamp)}`
              : "Not visible for this role"}
          </span>
        </div>
      </div>
    </Card>
  );
}
