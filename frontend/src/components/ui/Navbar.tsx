import { RoleSwitcher } from "./RoleSwitcher";

export function Navbar({ onMenuClick }: { onMenuClick: () => void }) {
  return (
    <header className="sticky top-0 z-20 flex items-center justify-between gap-4 border-b border-surface-700/60 bg-surface-950/90 px-4 py-3 backdrop-blur sm:px-6">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="focus-ring rounded-lg border border-surface-600 p-2 text-slate-300 hover:bg-surface-800 lg:hidden"
          aria-label="Toggle navigation"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18M3 12h18M3 18h18" strokeLinecap="round" />
          </svg>
        </button>
        <div className="flex flex-col leading-tight">
          <span className="text-sm font-semibold text-slate-100">Healthcare Claims Analytics Warehouse</span>
          <span className="text-[11px] text-slate-500">Claims Operations Command Center</span>
        </div>
      </div>
      <RoleSwitcher />
    </header>
  );
}
