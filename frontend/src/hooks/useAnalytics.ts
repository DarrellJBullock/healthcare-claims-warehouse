import { useEffect, useState } from "react";

import { ApiError } from "../lib/api";
import { useRole } from "./useRole";

interface AnalyticsState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/** Generic role-aware data-fetching hook used by every dashboard page.
 * Pass `deps` for extra values (page, filters, ...) that should trigger a refetch. */
export function useAnalytics<T>(
  fetcher: (role: ReturnType<typeof useRole>["role"]) => Promise<T>,
  deps: unknown[] = []
): AnalyticsState<T> {
  const { role } = useRole();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetcher(role)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Something went wrong loading this data.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role, tick, ...deps]);

  return { data, loading, error, refetch: () => setTick((t) => t + 1) };
}
