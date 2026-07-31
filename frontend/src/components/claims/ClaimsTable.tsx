import { MaskedIdentifier } from "../ui/MaskedIdentifier";
import { Table } from "../ui/Table";
import { formatCurrency, formatDate } from "../../lib/formatters";
import { ClaimStatusBadge } from "./ClaimStatusBadge";

export interface ClaimListItem {
  analytics_claim_key: number;
  claim_id: string;
  claim_status: string;
  claim_type: string;
  service_date_start: string;
  service_date_end: string;
  billed_amount: number;
  paid_amount: number;
  provider_name: string;
  payer_name: string;
  denial_reason: string | null;
}

export function ClaimsTable({
  claims,
  onSelect,
}: {
  claims: ClaimListItem[];
  onSelect: (analyticsClaimKey: number) => void;
}) {
  return (
    <Table
      keyField={(row) => row.analytics_claim_key}
      columns={[
        {
          header: "Claim ID",
          render: (row) => (
            <button onClick={() => onSelect(row.analytics_claim_key)} className="focus-ring rounded hover:underline">
              <MaskedIdentifier value={row.claim_id} />
            </button>
          ),
        },
        { header: "Status", render: (row) => <ClaimStatusBadge status={row.claim_status} /> },
        { header: "Type", render: (row) => row.claim_type },
        { header: "Provider", render: (row) => row.provider_name },
        { header: "Payer", render: (row) => row.payer_name },
        { header: "Service Date", render: (row) => formatDate(row.service_date_start) },
        { header: "Billed", render: (row) => formatCurrency(row.billed_amount), align: "right" },
        { header: "Paid", render: (row) => formatCurrency(row.paid_amount), align: "right" },
        { header: "Denial Reason", render: (row) => row.denial_reason ?? "—" },
      ]}
      rows={claims}
    />
  );
}
