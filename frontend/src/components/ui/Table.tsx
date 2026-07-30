import type { ReactNode } from "react";

export interface Column<T> {
  header: string;
  render: (row: T) => ReactNode;
  align?: "left" | "right" | "center";
  className?: string;
}

export function Table<T>({ columns, rows, keyField }: { columns: Column<T>[]; rows: T[]; keyField: (row: T) => string | number }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-surface-600/60">
      <table className="w-full min-w-[640px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-surface-600/60 bg-surface-800/60 text-left">
            {columns.map((col) => (
              <th
                key={col.header}
                className={`px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-400 ${
                  col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left"
                }`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={keyField(row)} className="border-b border-surface-700/40 last:border-0 hover:bg-surface-800/40">
              {columns.map((col) => (
                <td
                  key={col.header}
                  className={`px-4 py-3 text-slate-200 ${col.className ?? ""} ${
                    col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left"
                  }`}
                >
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
