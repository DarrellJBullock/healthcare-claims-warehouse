import type { Role } from "./roles";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown, message: string) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

async function request<T>(path: string, role: Role, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Demo-Role": role,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      // no JSON body
    }
    const message =
      (body as { detail?: string } | null)?.detail ?? `Request to ${path} failed with status ${response.status}`;
    throw new ApiError(response.status, body, message);
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("text/csv")) {
    return (await response.text()) as unknown as T;
  }
  return (await response.json()) as T;
}

export const api = {
  dashboardSummary: (role: Role) => request(`/dashboard/summary/`, role),
  claims: (role: Role, params: Record<string, string> = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/claims/${query ? `?${query}` : ""}`, role);
  },
  claimDetail: (role: Role, claimId: string) => request(`/claims/${encodeURIComponent(claimId)}/`, role),
  providerPerformance: (role: Role) => request(`/providers/performance/`, role),
  payerPerformance: (role: Role) => request(`/payers/performance/`, role),
  memberUtilization: (role: Role) => request(`/members/utilization/`, role),
  dataQualityResults: (role: Role) => request(`/data-quality/results/`, role),
  runDataQualityChecks: (role: Role) => request(`/data-quality/run/`, role, { method: "POST" }),
  complianceSummary: (role: Role) => request(`/compliance/summary/`, role),
  auditLog: (role: Role, params: Record<string, string> = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/audit-log/${query ? `?${query}` : ""}`, role);
  },
  aboutProject: (role: Role) => request(`/about/project/`, role),
  logRoleChanged: (role: Role) =>
    request(`/audit-log/role-changed/`, role, { method: "POST", body: JSON.stringify({ role }) }),
  createExport: (role: Role, exportType: string, reason: string) =>
    request<string>(`/exports/`, role, { method: "POST", body: JSON.stringify({ export_type: exportType, reason }) }),
};

export { API_BASE_URL };
