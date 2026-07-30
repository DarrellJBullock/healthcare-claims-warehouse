import { Card } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { DEMO_ROLES, getPermissions } from "../../lib/roles";

const CAPABILITIES: { key: keyof ReturnType<typeof getPermissions>; label: string }[] = [
  { key: "canViewRowLevelClaims", label: "Row-level claims" },
  { key: "canViewMemberDetail", label: "Member detail" },
  { key: "canViewDataQuality", label: "Data quality" },
  { key: "canViewCompliance", label: "Compliance" },
  { key: "canViewAuditLog", label: "Audit log" },
  { key: "canExport", label: "Exports" },
];

export function AccessControlMatrix() {
  return (
    <Card title="Role-Based Access Control Matrix">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[560px] border-collapse text-xs">
          <thead>
            <tr className="border-b border-surface-600/60 text-left text-slate-400">
              <th className="px-3 py-2">Role</th>
              {CAPABILITIES.map((cap) => (
                <th key={cap.key} className="px-3 py-2">{cap.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {DEMO_ROLES.map((role) => {
              const perms = getPermissions(role);
              return (
                <tr key={role} className="border-b border-surface-700/40 last:border-0">
                  <td className="px-3 py-2 font-medium text-slate-200">{role}</td>
                  {CAPABILITIES.map((cap) => (
                    <td key={cap.key} className="px-3 py-2">
                      {perms[cap.key] ? <Badge tone="success">Yes</Badge> : <Badge tone="neutral">No</Badge>}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
