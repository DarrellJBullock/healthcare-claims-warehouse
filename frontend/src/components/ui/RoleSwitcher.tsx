import { useRole } from "../../hooks/useRole";
import { DEMO_ROLES } from "../../lib/roles";

export function RoleSwitcher() {
  const { role, setRole } = useRole();

  return (
    <label className="flex items-center gap-2 text-xs text-slate-400">
      <span className="hidden sm:inline">Demo role</span>
      <select
        value={role}
        onChange={(e) => setRole(e.target.value as (typeof DEMO_ROLES)[number])}
        className="focus-ring rounded-lg border border-surface-600 bg-surface-800 px-3 py-1.5 text-sm font-medium text-slate-100"
        aria-label="Switch demo role"
      >
        {DEMO_ROLES.map((r) => (
          <option key={r} value={r}>
            {r}
          </option>
        ))}
      </select>
    </label>
  );
}
