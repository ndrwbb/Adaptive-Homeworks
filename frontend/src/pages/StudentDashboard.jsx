import { Link } from "react-router-dom";
import { useEffect } from "react";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";

export default function StudentDashboard() {
  const { loadStudentDashboard, loading, session, studentSnapshot } = useAppContext();
  useEffect(() => {
    loadStudentDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading.student && !studentSnapshot.dashboard) {
    return <Loader label="Preparing student dashboard..." />;
  }

  const dashboard = studentSnapshot.dashboard;
  const progress = studentSnapshot.progress;
  const practiceTask = studentSnapshot.practiceTask;
  const nearestDeadline = dashboard?.homeworks?.nearestDeadline;

  if (!progress || !dashboard) {
    return null;
  }

  return (
    <section className="stack">
      <div className="hero-card">
        <span className="eyebrow">Student workspace</span>
        <h1>Welcome back, {session?.user?.full_name}.</h1>
        <p>
          Your learning flow is split into teacher-assigned homeworks and independent self-education.
          Use this page to switch between both modes and track the current adaptive baseline.
        </p>

        <div className="hero-card__actions">
          <Link to="/student/homeworks" className="primary-button">
            Open homeworks
          </Link>
          <Link to="/student/self-education" className="ghost-button ghost-button--light">
            Start self-education
          </Link>
        </div>
      </div>

      <div className="stats-grid">
        {dashboard.overview.map((item) => (
          <StatCard key={item.label} label={item.label} value={item.value} note={item.note} />
        ))}
      </div>

      <div className="workspace-grid">
        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow">Homework mode</span>
              <h2>Assigned learning path</h2>
            </div>
            <span className="difficulty-badge">{dashboard.homeworks.activeCount} active</span>
          </div>
          <p>
            Continue teacher-assigned homeworks, monitor deadlines, and see which assignments still
            need review or submission.
          </p>
          <div className="panel__meta">
            <span>
              {nearestDeadline
                ? `Nearest deadline: ${new Date(nearestDeadline.deadline).toLocaleString()}`
                : "No upcoming deadlines"}
            </span>
            <Link to="/student/homeworks">Open homeworks</Link>
          </div>
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <span className="eyebrow">Self-Education mode</span>
              <h2>{practiceTask?.title || "Practice recommendation pending"}</h2>
            </div>
            <span className="difficulty-badge">
              {practiceTask ? `Level ${practiceTask.difficulty}` : "Waiting"}
            </span>
          </div>
          <p>
            {practiceTask?.body ||
              "Choose subject and difficulty, then work through auto-graded practice tasks."}
          </p>
          <div className="panel__meta">
            <span>{practiceTask?.topic || "adaptive practice"}</span>
            <Link to="/student/self-education">Open self-education</Link>
          </div>
        </article>
      </div>

      <article className="panel">
        <div className="panel__header">
          <div>
            <span className="eyebrow">Recent activity</span>
            <h2>Submission timeline</h2>
          </div>
          <Link to="/student/progress">Open analytics</Link>
        </div>
        <ul className="timeline">
          {dashboard.recentSubmissions.length > 0 ? (
            dashboard.recentSubmissions.map((submission) => (
              <li key={submission.submission_id} className="timeline__item">
                <div className={`timeline__marker ${submission.is_correct ? "timeline__marker--good" : ""}`} />
                <div>
                  <strong>{submission.task_title}</strong>
                  <p>
                    {submission.topic} · {submission.is_correct ? "Correct" : "Needs revision"} ·{" "}
                    {submission.score_delta > 0 ? `+${submission.score_delta}` : submission.score_delta}
                  </p>
                </div>
              </li>
            ))
          ) : (
            <li className="timeline__item">
              <div className="timeline__marker" />
              <div>
                <strong>No recent submissions yet</strong>
                <p>Start with a homework or self-education task to populate analytics.</p>
              </div>
            </li>
          )}
        </ul>
      </article>
    </section>
  );
}

function StatCard({ label, note, value }) {
  return (
    <article className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{note}</p>
    </article>
  );
}
