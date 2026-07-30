import { useState } from "react";
import type { ReactNode } from "react";

import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

export function SyntheticDataBanner() {
  return (
    <div className="border-b border-accent-500/20 bg-accent-500/5 px-4 py-2 text-center text-xs font-medium text-accent-400 sm:px-6">
      Synthetic data only. No real PHI is used in this portfolio project.
    </div>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen">
      <Navbar onMenuClick={() => setMobileOpen((v) => !v)} />
      <SyntheticDataBanner />
      <div className="mx-auto flex max-w-[1600px]">
        <aside className="sticky top-[89px] hidden h-[calc(100vh-89px)] w-60 shrink-0 border-r border-surface-700/60 lg:block">
          <Sidebar />
        </aside>

        {mobileOpen && (
          <div className="fixed inset-0 z-30 flex lg:hidden">
            <div className="w-64 border-r border-surface-700/60 bg-surface-950">
              <Sidebar onNavigate={() => setMobileOpen(false)} />
            </div>
            <button
              className="flex-1 bg-black/60"
              aria-label="Close navigation"
              onClick={() => setMobileOpen(false)}
            />
          </div>
        )}

        <main className="min-w-0 flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
