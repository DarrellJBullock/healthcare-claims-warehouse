export function MaskedIdentifier({ value }: { value: string | null | undefined }) {
  if (!value) return <span className="text-slate-500">—</span>;
  const isMasked = value.includes("•");
  return (
    <span className={`font-mono text-xs ${isMasked ? "text-slate-400" : "text-slate-200"}`} title={isMasked ? "Masked identifier" : undefined}>
      {value}
    </span>
  );
}
