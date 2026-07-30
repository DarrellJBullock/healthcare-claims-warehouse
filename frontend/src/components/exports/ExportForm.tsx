import { useState } from "react";

import { api, ApiError } from "../../lib/api";
import { canExportType, type Role } from "../../lib/roles";
import { Button } from "../ui/Button";
import { filterInputClass } from "../ui/FilterBar";
import { ExportOptionCard } from "./ExportOptionCard";

const EXPORT_OPTIONS: { type: string; title: string; description: string }[] = [
  { type: "aggregate_claims", title: "Aggregate Claims Export", description: "Monthly claim totals, billed/paid amounts, denial rate. No row-level or member data." },
  { type: "masked_claims", title: "Masked Claims Export", description: "Row-level claims with masked claim identifiers. For Claims Analysts and Admins." },
  { type: "data_quality_report", title: "Data Quality Report", description: "Latest data quality check results across all tables. For Data Engineers and Admins." },
  { type: "audit_report", title: "Audit Report", description: "Recent audit log events for compliance review. For Auditors and Admins." },
];

function downloadCsv(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function ExportForm({ role }: { role: Role }) {
  const [selected, setSelected] = useState<string>(EXPORT_OPTIONS[0].type);
  const [reason, setReason] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("loading");
    setMessage(null);
    try {
      const content = await api.createExport(role, selected, reason);
      downloadCsv(`${selected}.csv`, content);
      setStatus("success");
      setMessage("Export generated and downloaded. An audit event was recorded.");
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof ApiError ? err.message : "Export failed.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {EXPORT_OPTIONS.map((option) => (
          <ExportOptionCard
            key={option.type}
            title={option.title}
            description={option.description}
            allowed={canExportType(role, option.type)}
            selected={selected === option.type}
            onSelect={() => setSelected(option.type)}
          />
        ))}
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-xs font-medium text-slate-400" htmlFor="export-reason">
          Export reason (required)
        </label>
        <textarea
          id="export-reason"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="e.g. Quarterly finance reconciliation report"
          className={`${filterInputClass} min-h-[80px] w-full`}
          required
        />
      </div>

      <div className="flex items-center gap-3">
        <Button type="submit" disabled={status === "loading" || !canExportType(role, selected)}>
          {status === "loading" ? "Generating…" : "Generate Export"}
        </Button>
        {message && (
          <span className={`text-xs ${status === "error" ? "text-risk-critical" : "text-risk-low"}`}>{message}</span>
        )}
      </div>
    </form>
  );
}
