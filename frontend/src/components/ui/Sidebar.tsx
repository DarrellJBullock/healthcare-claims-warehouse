import { NavLink } from "react-router-dom";

import { useRole } from "../../hooks/useRole";
import { getPermissions } from "../../lib/roles";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", end: true, requires: null as null | keyof ReturnType<typeof getPermissions> },
  { to: "/claims", label: "Claims", requires: "canViewRowLevelClaims" as const },
  { to: "/providers", label: "Providers", requires: null },
  { to: "/payers", label: "Payers", requires: null },
  { to: "/members", label: "Members", requires: null },
  { to: "/data-quality", label: "Data Quality", requires: "canViewDataQuality" as const },
  { to: "/compliance", label: "Compliance", requires: null },
  { to: "/audit-log", label: "Audit Log", requires: "canViewAuditLog" as const },
  { to: "/exports", label: "Exports", requires: null },
  { to: "/about", label: "About", requires: null },
];

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const { role } = useRole();
  const permissions = getPermissions(role);

  return (
    <nav className="flex h-full flex-col gap-1 p-3">
      {NAV_ITEMS.map((item) => {
        const locked = item.requires && !permissions[item.requires];
        return (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            className={({ isActive }) =>
              `focus-ring flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-accent-500/15 text-accent-400"
                  : locked
                    ? "text-slate-600"
                    : "text-slate-300 hover:bg-surface-800 hover:text-slate-100"
              }`
            }
          >
            <span>{item.label}</span>
            {locked && <span className="text-[10px] uppercase tracking-wide text-slate-600">Restricted</span>}
          </NavLink>
        );
      })}
    </nav>
  );
}
