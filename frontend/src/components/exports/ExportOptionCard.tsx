import { Badge } from "../ui/Badge";

export function ExportOptionCard({
  title,
  description,
  allowed,
  selected,
  onSelect,
}: {
  title: string;
  description: string;
  allowed: boolean;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      disabled={!allowed}
      onClick={onSelect}
      className={`focus-ring flex flex-col gap-2 rounded-xl border p-4 text-left transition-colors disabled:cursor-not-allowed disabled:opacity-40 ${
        selected ? "border-accent-500 bg-accent-500/10" : "border-surface-600 bg-surface-850 hover:bg-surface-800"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-100">{title}</span>
        {!allowed && <Badge tone="neutral">Not permitted</Badge>}
      </div>
      <p className="text-xs text-slate-400">{description}</p>
    </button>
  );
}
