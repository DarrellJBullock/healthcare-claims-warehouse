export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-surface-600 py-12 text-center">
      <p className="text-sm font-medium text-slate-300">{title}</p>
      {description && <p className="max-w-sm text-xs text-slate-500">{description}</p>}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-risk-critical/30 bg-risk-critical/5 py-12 text-center">
      <p className="text-sm font-medium text-risk-critical">Failed to load data</p>
      <p className="max-w-sm text-xs text-slate-400">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="focus-ring mt-1 rounded-lg border border-surface-600 px-3 py-1.5 text-xs text-slate-200 hover:bg-surface-800">
          Retry
        </button>
      )}
    </div>
  );
}
