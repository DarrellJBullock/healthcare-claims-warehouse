import { Card } from "../components/ui/Card";
import { ErrorState } from "../components/ui/EmptyState";
import { Skeleton } from "../components/ui/Skeleton";
import { useAnalytics } from "../hooks/useAnalytics";
import { api } from "../lib/api";

interface AboutProjectResponse {
  project_name: string;
  portfolio_angle: string;
  synthetic_data_notice: string;
  hipaa_aware_disclaimer: string;
  architecture: string[];
  data_model_summary: string;
  roadmap: string[];
}

export function About() {
  const { data, loading, error, refetch } = useAnalytics<AboutProjectResponse>((role) =>
    api.aboutProject(role) as Promise<AboutProjectResponse>
  );

  if (loading) {
    return (
      <div className="flex flex-col gap-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (error || !data) {
    return <ErrorState message={error ?? "No data available."} onRetry={refetch} />;
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">{data.project_name}</h1>
        <p className="mt-1 text-sm text-slate-400">{data.portfolio_angle}</p>
      </div>

      <Card title="Synthetic Data &amp; HIPAA-Aware Design">
        <p className="text-sm text-accent-400">{data.synthetic_data_notice}</p>
        <p className="mt-3 text-xs leading-relaxed text-slate-400">{data.hipaa_aware_disclaimer}</p>
      </Card>

      <Card title="Architecture">
        <ul className="flex flex-col gap-2 text-sm text-slate-300">
          {data.architecture.map((line) => (
            <li key={line} className="flex gap-2">
              <span className="text-accent-500">→</span>
              <span>{line}</span>
            </li>
          ))}
        </ul>
      </Card>

      <Card title="Data Model Summary">
        <p className="text-sm text-slate-300">{data.data_model_summary}</p>
      </Card>

      <Card title="Future Roadmap">
        <ul className="flex flex-col gap-2 text-sm text-slate-300">
          {data.roadmap.map((line) => (
            <li key={line} className="flex gap-2">
              <span className="text-slate-600">•</span>
              <span>{line}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
