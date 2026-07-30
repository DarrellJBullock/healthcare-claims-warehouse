import { AccessControlMatrix } from "../components/compliance/AccessControlMatrix";
import { ComplianceChecklist } from "../components/compliance/ComplianceChecklist";
import { MaskingStatusCard } from "../components/compliance/MaskingStatusCard";
import { RetentionPolicyCard } from "../components/compliance/RetentionPolicyCard";
import { Card } from "../components/ui/Card";
import { ErrorState } from "../components/ui/EmptyState";
import { SkeletonGrid } from "../components/ui/Skeleton";
import { useAnalytics } from "../hooks/useAnalytics";
import { api } from "../lib/api";
import { formatDateTime } from "../lib/formatters";

interface ComplianceSummaryResponse {
  synthetic_data_only: boolean;
  phi_risk_status: string;
  retention_policy: { raw_synthetic_uploads_days: number; curated_analytics_days: number; audit_log_years: number };
  last_export: { timestamp: string; role: string; resource_id: string } | null;
  last_sensitive_view_event: { timestamp: string; role: string; action: string } | null;
  failed_access_attempts_last_30_days: number;
  checklist: { item: string; status: string }[];
}

export function Compliance() {
  const { data, loading, error, refetch } = useAnalytics<ComplianceSummaryResponse>((role) =>
    api.complianceSummary(role) as Promise<ComplianceSummaryResponse>
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">Compliance Dashboard</h1>
        <p className="text-sm text-slate-500">Synthetic data only. No real PHI is used in this portfolio project.</p>
      </div>

      {loading && <SkeletonGrid />}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {!loading && !error && data && (
        <>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <MaskingStatusCard phiRiskStatus={data.phi_risk_status} lastSensitiveViewEvent={data.last_sensitive_view_event} />
            <RetentionPolicyCard policy={data.retention_policy} />
            <Card title="Export &amp; Access Activity">
              <div className="flex flex-col gap-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Last export</span>
                  <span className="text-slate-200">
                    {data.last_export ? `${data.last_export.resource_id} · ${formatDateTime(data.last_export.timestamp)}` : "Not visible for this role"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Failed access attempts (30d)</span>
                  <span className="text-slate-200">{data.failed_access_attempts_last_30_days}</span>
                </div>
              </div>
            </Card>
          </div>

          <ComplianceChecklist items={data.checklist} />
          <AccessControlMatrix />
        </>
      )}
    </div>
  );
}
