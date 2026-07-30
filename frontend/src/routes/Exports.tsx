import { ExportForm } from "../components/exports/ExportForm";
import { Card } from "../components/ui/Card";
import { useRole } from "../hooks/useRole";

export function Exports() {
  const { role } = useRole();

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-100">Exports</h1>
        <p className="text-sm text-slate-500">
          Every export requires a role check, a stated reason, and creates an audit trail entry. Row-level exports are
          masked by default.
        </p>
      </div>

      <Card title={`Export as ${role}`}>
        <ExportForm role={role} />
      </Card>
    </div>
  );
}
