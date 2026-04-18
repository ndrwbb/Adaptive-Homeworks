import { Link, Navigate } from "react-router-dom";
import { useAppContext } from "../context/AppContext";

export default function Home() {
  const { session } = useAppContext();

  if (session) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <section className="stack">
      <div className="hero-card hero-card--landing">
        <div className="hero-card__copy">
          <span className="eyebrow">Adaptive EdTech system</span>
          <h1>Web application for adaptive homework assignment and student progress analysis.</h1>
          <p>
            This MVP combines a substantial FastAPI backend with a role-based frontend demo that already
            covers the main student and teacher scenarios at the current ~60% checkpoint.
          </p>

          <div className="hero-card__actions">
            <Link to="/login" className="primary-button">
              Open demo
            </Link>
            <Link to="/register" className="ghost-button ghost-button--light">
              Create account
            </Link>
          </div>
        </div>

        <div className="feature-stack">
          <article className="feature-chip">
            <strong>Backend</strong>
            <span>Auth, roles, tasks, submissions, progress, teacher endpoints</span>
          </article>
          <article className="feature-chip">
            <strong>Frontend</strong>
            <span>Student and teacher workspaces with fallback-ready data flows</span>
          </article>
          <article className="feature-chip">
            <strong>Next stage</strong>
            <span>Advanced ML personalization, richer analytics, evaluation, testing</span>
          </article>
        </div>
      </div>

      <div className="workspace-grid">
        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow">Demo access</span>
              <h2>Ready-made accounts</h2>
            </div>
          </div>
          <ul className="checklist">
            <li>
              <strong>Student:</strong> `student@example.com` / `demo123`
            </li>
            <li>
              <strong>Teacher:</strong> `teacher@example.com` / `demo123`
            </li>
            <li>
              If the backend is unavailable, the same accounts still open the interface in demo mode.
            </li>
          </ul>
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow">Implemented now</span>
              <h2>Current project slice</h2>
            </div>
          </div>
          <ul className="checklist">
            <li>JWT authentication and role-aware access control</li>
            <li>Adaptive task recommendation based on baseline skill score</li>
            <li>Submission processing and skill score updates</li>
            <li>Student dashboards and teacher analytics workspace</li>
          </ul>
        </article>
      </div>
    </section>
  );
}
