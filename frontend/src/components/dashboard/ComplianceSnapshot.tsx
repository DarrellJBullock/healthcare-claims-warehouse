import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";

export function ComplianceSnapshot({
  compliance,
  openDataQualityIssues,
}: {
  compliance: Record<string, boolean>;
  openDataQualityIssues: number;
}) {
  const rows: [string, boolean][] = [
    ["Masking enabled", compliance.masking_enabled],
    ["Audit logging enabled", compliance.audit_logging_enabled],
    ["Export controls enabled", compliance.export_controls_enabled],
    ["Role-based access enabled", compliance.role_based_access_enabled],
  ];

  return (
    <Card title="Compliance Snapshot">
      <div className="flex flex-col gap-2.5">
        {rows.map(([label, enabled]) => (
          <div key={label} className="flex items-center justify-between text-xs">
            <span className="text-slate-400">{label}</span>
            <Badge tone={enabled ? "success" : "danger"}>{enabled ? "Enabled" : "Disabled"}</Badge>
          </div>
        ))}
        <div className="flex items-center justify-between border-t border-surface-700/60 pt-2.5 text-xs">
          <span className="text-slate-400">Open data quality issues</span>
          <Badge tone={openDataQualityIssues > 0 ? "warning" : "success"}>{openDataQualityIssues}</Badge>
        </div>
      </div>
    </Card>
  );
}
