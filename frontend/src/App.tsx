import { Routes, Route } from "react-router-dom";
import { Layout } from "./Layout";
import { Dashboard } from "./pages/Dashboard";
import { AgentRunner } from "./pages/AgentRunner";
import { EventStream } from "./pages/EventStream";
import { Policies } from "./pages/Policies";
import { AuditLog } from "./pages/AuditLog";
import { Documentation } from "./pages/Documentation";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="agent-runner" element={<AgentRunner />} />
        <Route path="event-stream" element={<EventStream />} />
        <Route path="policies" element={<Policies />} />
        <Route path="audit-log" element={<AuditLog />} />
        <Route path="documentation" element={<Documentation />} />
      </Route>
    </Routes>
  );
}

export default App;
