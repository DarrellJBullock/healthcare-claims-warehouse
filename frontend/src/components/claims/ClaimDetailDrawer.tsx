import { useEffect, useState } from "react";

import { api } from "../../lib/api";
import { formatCurrency, formatDate } from "../../lib/formatters";
import { useRole } from "../../hooks/useRole";
import { Badge } from "../ui/Badge";
import { MaskedIdentifier } from "../ui/MaskedIdentifier";
import { Skeleton } from "../ui/Skeleton";
import { ClaimStatusBadge } from "./ClaimStatusBadge";

interface ClaimDetail {
  claim_id: string;
  member_id: string;
  claim_status: string;
  claim_type: string;
  service_date_start: string;
  service_date_end: string;
  submitted_date: string;
  billed_amount: number;
  paid_amount: number;
  provider_name: string;
  payer_name: string;
  denial_reason: string | null;
  diagnosis_category_name: string | null;
  service_lines: {
    line_number: number;
    procedure_category_name: string | null;
    units: number;
    billed_amount: number;
    allowed_amount: number;
    paid_amount: number;
  }[];
}

export function ClaimDetailDrawer({
  analyticsClaimKey,
  onClose,
}: {
  analyticsClaimKey: number;
  onClose: () => void;
}) {
  const { role } = useRole();
  const [claim, setClaim] = useState<ClaimDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setClaim(null);
    setError(null);
    api
      .claimDetail(role, analyticsClaimKey)
      .then((data) => setClaim(data as ClaimDetail))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load claim."));
  }, [analyticsClaimKey, role]);

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <button className="flex-1 bg-black/60" aria-label="Close claim detail" onClick={onClose} />
      <div className="h-full w-full max-w-lg overflow-y-auto border-l border-surface-600 bg-surface-900 p-6">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-100">Claim Detail</h2>
          <button onClick={onClose} className="focus-ring rounded-lg border border-surface-600 px-2 py-1 text-xs text-slate-300 hover:bg-surface-800">
            Close
          </button>
        </div>

        {error && (
          <div className="rounded-lg border border-risk-critical/30 bg-risk-critical/5 p-4 text-sm text-risk-critical">{error}</div>
        )}

        {!claim && !error && (
          <div className="flex flex-col gap-3">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-40 w-full" />
          </div>
        )}

        {claim && (
          <div className="flex flex-col gap-5">
            <div>
              <MaskedIdentifier value={claim.claim_id} />
              <div className="mt-2 flex items-center gap-2">
                <ClaimStatusBadge status={claim.claim_status} />
                <Badge tone="neutral">{claim.claim_type}</Badge>
              </div>
            </div>

            <dl className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <dt className="text-slate-500">Member</dt>
                <dd><MaskedIdentifier value={claim.member_id} /></dd>
              </div>
              <div>
                <dt className="text-slate-500">Diagnosis</dt>
                <dd className="text-slate-200">{claim.diagnosis_category_name ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Provider</dt>
                <dd className="text-slate-200">{claim.provider_name}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Payer</dt>
                <dd className="text-slate-200">{claim.payer_name}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Service Dates</dt>
                <dd className="text-slate-200">
                  {formatDate(claim.service_date_start)} – {formatDate(claim.service_date_end)}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Submitted</dt>
                <dd className="text-slate-200">{formatDate(claim.submitted_date)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Billed</dt>
                <dd className="text-slate-200">{formatCurrency(claim.billed_amount)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Paid</dt>
                <dd className="text-slate-200">{formatCurrency(claim.paid_amount)}</dd>
              </div>
              {claim.denial_reason && (
                <div className="col-span-2">
                  <dt className="text-slate-500">Denial Reason</dt>
                  <dd className="text-risk-critical">{claim.denial_reason}</dd>
                </div>
              )}
            </dl>

            <div>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Service Lines</h3>
              <div className="flex flex-col gap-2">
                {claim.service_lines.map((line) => (
                  <div key={line.line_number} className="rounded-lg border border-surface-700/60 p-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-200">{line.procedure_category_name ?? "Unknown procedure"}</span>
                      <span className="text-slate-500">x{line.units}</span>
                    </div>
                    <div className="mt-1 flex items-center justify-between text-slate-400">
                      <span>Billed {formatCurrency(line.billed_amount)}</span>
                      <span>Allowed {formatCurrency(line.allowed_amount)}</span>
                      <span>Paid {formatCurrency(line.paid_amount)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
