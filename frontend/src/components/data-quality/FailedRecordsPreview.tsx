import { Card } from "../ui/Card";
import { EmptyState } from "../ui/EmptyState";
import { MaskedIdentifier } from "../ui/MaskedIdentifier";
import type { DataQualityResultRow } from "./QualityChecksTable";

export function FailedRecordsPreview({ rows }: { rows: DataQualityResultRow[] }) {
  const failing = rows.filter((row) => row.status === "FAIL");

  return (
    <Card title="Failed Checks — Sample Records (Masked)">
      {failing.length === 0 ? (
        <EmptyState title="No failing checks" description="Every data quality check is currently passing." />
      ) : (
        <ul className="flex flex-col divide-y divide-surface-700/50">
          {failing.map((row) => (
            <li key={row.check_name} className="flex items-center justify-between gap-3 py-2.5 text-xs">
              <div className="flex flex-col">
                <span className="font-medium text-slate-200">{row.check_name}</span>
                <span className="text-slate-500">{row.message}</span>
              </div>
              <MaskedIdentifier value={row.sample_record_key} />
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
