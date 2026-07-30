export const DEMO_ROLES = [
  "Admin",
  "Data Engineer",
  "Claims Analyst",
  "Manager",
  "Auditor",
  "Read Only",
] as const;

export type Role = (typeof DEMO_ROLES)[number];

export const DEFAULT_ROLE: Role = "Read Only";

export interface RolePermissions {
  role: Role;
  canViewRowLevelClaims: boolean;
  canViewMemberDetail: boolean;
  canViewAggregateOnly: boolean;
  canViewDataQuality: boolean;
  canViewCompliance: boolean;
  canViewAuditLog: boolean;
  canRunQualityChecks: boolean;
  canExport: boolean;
  canManageRoleControls: boolean;
  maskIdentifiers: boolean;
}

/** Mirrors backend/apps/warehouse/services/roles.py so the UI can hide
 * routes/actions client-side; the API is the real enforcement boundary. */
export function getPermissions(role: Role): RolePermissions {
  return {
    role,
    canViewRowLevelClaims: ["Admin", "Claims Analyst", "Data Engineer"].includes(role),
    canViewMemberDetail: ["Admin", "Claims Analyst"].includes(role),
    canViewAggregateOnly: ["Manager", "Read Only"].includes(role),
    canViewDataQuality: ["Admin", "Data Engineer"].includes(role),
    canViewCompliance: ["Admin", "Auditor"].includes(role),
    canViewAuditLog: ["Admin", "Auditor"].includes(role),
    canRunQualityChecks: ["Admin", "Data Engineer"].includes(role),
    canExport: ["Admin", "Manager", "Data Engineer", "Claims Analyst", "Auditor"].includes(role),
    canManageRoleControls: role === "Admin",
    maskIdentifiers: role !== "Admin",
  };
}

const EXPORT_TYPES: Record<string, Role[]> = {
  aggregate_claims: ["Admin", "Manager", "Data Engineer", "Claims Analyst", "Auditor"],
  masked_claims: ["Admin", "Claims Analyst"],
  data_quality_report: ["Admin", "Data Engineer"],
  audit_report: ["Admin", "Auditor"],
};

export function canExportType(role: Role, exportType: string): boolean {
  return EXPORT_TYPES[exportType]?.includes(role) ?? false;
}

export const ROLE_STORAGE_KEY = "hcw:selected-role";
