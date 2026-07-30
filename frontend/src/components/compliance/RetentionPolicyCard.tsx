import { Card } from "../ui/Card";

export function RetentionPolicyCard({
  policy,
}: {
  policy: { raw_synthetic_uploads_days: number; curated_analytics_days: number; audit_log_years: number };
}) {
  const rows = [
    { label: "Raw synthetic uploads", value: `${policy.raw_synthetic_uploads_days} days` },
    { label: "Curated analytics", value: `${policy.curated_analytics_days} days` },
    { label: "Audit logs", value: `${policy.audit_log_years} years` },
  ];

  return (
    <Card title="Retention Policy (Demo Setting)">
      <div className="flex flex-col gap-2.5">
        {rows.map((row) => (
          <div key={row.label} className="flex items-center justify-between text-xs">
            <span className="text-slate-400">{row.label}</span>
            <span className="font-medium text-slate-200">{row.value}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
