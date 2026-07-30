import { Route, Routes } from "react-router-dom";

import { AppShell } from "./components/ui/AppShell";
import { RoleProvider } from "./hooks/useRole";
import { About } from "./routes/About";
import { AuditLog } from "./routes/AuditLog";
import { Claims } from "./routes/Claims";
import { Compliance } from "./routes/Compliance";
import { Dashboard } from "./routes/Dashboard";
import { DataQuality } from "./routes/DataQuality";
import { Exports } from "./routes/Exports";
import { Members } from "./routes/Members";
import { Payers } from "./routes/Payers";
import { Providers } from "./routes/Providers";

export default function App() {
  return (
    <RoleProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/claims" element={<Claims />} />
          <Route path="/providers" element={<Providers />} />
          <Route path="/payers" element={<Payers />} />
          <Route path="/members" element={<Members />} />
          <Route path="/data-quality" element={<DataQuality />} />
          <Route path="/compliance" element={<Compliance />} />
          <Route path="/audit-log" element={<AuditLog />} />
          <Route path="/exports" element={<Exports />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </AppShell>
    </RoleProvider>
  );
}
