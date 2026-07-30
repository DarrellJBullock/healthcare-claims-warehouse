import type { ReactNode } from "react";

export function FilterBar({ children }: { children: ReactNode }) {
  return (
    <div className="panel flex flex-wrap items-end gap-3 p-4">
      {children}
    </div>
  );
}

export function FilterField({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1 text-xs font-medium text-slate-400">
      {label}
      {children}
    </label>
  );
}

export const filterInputClass =
  "focus-ring rounded-lg border border-surface-600 bg-surface-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500";
