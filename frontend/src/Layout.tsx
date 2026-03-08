import { Outlet, NavLink } from "react-router-dom";

export function Layout() {
  return (
    <div className="app">
      <aside className="sidebar">
        <p className="sidebar-title">AgentOps</p>
        <nav>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/agent-runner">Agent Runner</NavLink>
          <NavLink to="/event-stream">Event Stream</NavLink>
          <NavLink to="/policies">Policies</NavLink>
          <NavLink to="/audit-log">Audit Log</NavLink>
          <NavLink to="/documentation">Documentation</NavLink>
        </nav>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
