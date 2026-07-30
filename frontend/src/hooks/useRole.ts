import { createContext, createElement, useCallback, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { api } from "../lib/api";
import { DEFAULT_ROLE, ROLE_STORAGE_KEY, type Role } from "../lib/roles";

interface RoleContextValue {
  role: Role;
  setRole: (role: Role) => void;
}

const RoleContext = createContext<RoleContextValue | null>(null);

function readStoredRole(): Role {
  if (typeof window === "undefined") return DEFAULT_ROLE;
  const stored = window.localStorage.getItem(ROLE_STORAGE_KEY);
  return (stored as Role) || DEFAULT_ROLE;
}

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRoleState] = useState<Role>(readStoredRole);

  const setRole = useCallback((next: Role) => {
    setRoleState(next);
    window.localStorage.setItem(ROLE_STORAGE_KEY, next);
    api.logRoleChanged(next).catch(() => {
      // Best-effort demo audit log -- never block the UI on this.
    });
  }, []);

  const value = useMemo(() => ({ role, setRole }), [role, setRole]);

  return createElement(RoleContext.Provider, { value }, children);
}

export function useRole(): RoleContextValue {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error("useRole must be used within a RoleProvider");
  }
  return context;
}
