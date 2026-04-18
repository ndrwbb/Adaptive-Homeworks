import { NavLink, Outlet } from "react-router-dom";

import { useAppContext } from "../context/AppContext";
import Toast from "./Toast";

function roleLinks(role) {
  if (role === "student") {
    return [
      { to: "/dashboard", label: "Dashboard" },
      { to: "/student/homeworks", label: "Homeworks" },
      { to: "/student/self-education", label: "Self-Education" },
      { to: "/student/progress", label: "Progress" },
    ];
  }

  if (role === "teacher") {
    return [
      { to: "/dashboard", label: "Dashboard" },
      { to: "/teacher/homeworks", label: "Homeworks" },
      { to: "/teacher/tasks", label: "Task Bank" },
      { to: "/teacher/students", label: "Students" },
    ];
  }

  return [
    { to: "/login", label: "Login" },
    { to: "/register", label: "Register" },
  ];
}

export default function Layout() {
  const { backendMode, clearToast, logout, session, toast } = useAppContext();
  const links = roleLinks(session?.user?.role);

  return (
    <>
      <div className="shell">
        <header className="topbar">
          <NavLink to="/" className="brandmark">
            <span className="brandmark__eyebrow">EdTech MVP</span>
            <span className="brandmark__title">Adaptive Homework Studio</span>
          </NavLink>

          <nav className="nav">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => `nav__link${isActive ? " nav__link--active" : ""}`}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>

          <div className="topbar__meta">
            <span className={`status-pill status-pill--${backendMode}`}>
              {backendMode === "live" ? "Live API" : backendMode === "demo" ? "Demo Fallback" : "Checking API"}
            </span>
            {session ? (
              <button type="button" className="ghost-button" onClick={logout}>
                Logout
              </button>
            ) : null}
          </div>
        </header>

        <main className="page-frame">
          <Outlet />
        </main>
      </div>

      <Toast toast={toast} onDismiss={clearToast} />
    </>
  );
}
