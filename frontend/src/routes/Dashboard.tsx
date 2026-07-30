import { api } from "../lib/api";
import { useAnalytics } from "../hooks/useAnalytics";
import { ClaimsTrend } from "../components/dashboard/ClaimsTrend";
import { ComplianceSnapshot } from "../components/dashboard/ComplianceSnapshot";
import { DenialSummary } from "../components/dashboard/DenialSummary";
import { KpiGrid } from "../components/dashboard/KpiGrid";
import { RecentAuditEvents } from "../components/dashboard/RecentAuditEvents";
import { ErrorState } from "../components/ui/EmptyState";
import { SkeletonGrid } from "../components/ui/Skeleton";

interface DashboardSummaryResponse {
  total_claims: number;
  total_billed: number;
  total_paid: number;
  avg_paid_amount: number;
  denial_rate: number;
  top_denial_reason: string | null;
  open_data_quality_issues: number;
  recent_audit_events: {
    event_timestamp: string;
    user_role: string;
    action: string;
    resource_type: string;
    status: string;
  }[];
  compliance_status: Record<string, boolean>;
  monthly_trend: { month_date: string; total_claims: number; total_billed: number; total_paid: number }[];
  synthetic_data_notice: string;
}

export function Dashboard() {
  const { data, loading, error, refetch } = useAnalytics<DashboardSummaryResponse>((role) =>
    api.dashboardSummary(role) as Promise<DashboardSummaryResponse>
  );

  if (loading) {
    return (
      <div className="flex flex-col gap-6">
        <SkeletonGrid />
      </div>
    );
  }

  if (error || !data) {
    return <ErrorState message={error ?? "No data available."} onRetry={refetch} />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">Dashboard</h1>
        <p className="text-sm text-slate-500">Claims operations overview across all payers and providers.</p>
      </div>

      <KpiGrid summary={data} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ClaimsTrend data={data.monthly_trend} />
        </div>
        <DenialSummary denialRate={data.denial_rate} topReason={data.top_denial_reason} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <RecentAuditEvents events={data.recent_audit_events} />
        <ComplianceSnapshot compliance={data.compliance_status} openDataQualityIssues={data.open_data_quality_issues} />
      </div>
    </div>
  );
}
