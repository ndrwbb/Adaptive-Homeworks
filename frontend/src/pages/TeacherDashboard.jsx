import { Link } from "react-router-dom";
import { useEffect, useEffectEvent } from "react";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";

export default function TeacherDashboard() {
  const { loadTeacherDashboard, loading, teacherSnapshot } = useAppContext();
  const onLoad = useEffectEvent(() => {
    loadTeacherDashboard();
  });

  useEffect(() => {
    onLoad();
  }, [onLoad]);

  if (loading.teacher && teacherSnapshot.students.length === 0) {
    return <Loader label="Loading teacher workspace..." />;
  }

  return (
    <section className="stack">
      <div className="hero-card">
        <span className="eyebrow">Teacher hub</span>
        <h1>Monitor the cohort and manage assigned homeworks.</h1>
        <p>
          This workspace combines homework creation, reusable task banking, student tracking, and
          the current baseline adaptive state of the system.
        </p>

        <div className="hero-card__actions">
          <Link to="/teacher/homeworks" className="primary-button">
            New Homework
          </Link>
          <Link to="/teacher/tasks" className="ghost-button ghost-button--light">
            Open task bank
          </Link>
        </div>
      </div>

      <div className="stats-grid">
        {teacherSnapshot.stats.map((stat) => (
          <article className="stat-card" key={stat.label}>
            <span>{stat.label}</span>
            <strong>{stat.value}</strong>
            <p>{stat.note}</p>
          </article>
        ))}
      </div>

      <article className="panel">
        <div className="panel__header">
          <div>
            <span className="eyebrow">Student overview</span>
            <h2>Current cohort snapshot</h2>
          </div>
          <Link to="/teacher/students">Open analytics</Link>
        </div>

        <div className="student-grid">
          {teacherSnapshot.students.map((student) => (
            <article key={student.id} className="student-card">
              <strong>{student.full_name}</strong>
              <p>{student.email}</p>
              <div className="student-card__stats">
                <span>Skill {student.skill_score}</span>
                <span>{student.total_attempts} attempts</span>
              </div>
            </article>
          ))}
        </div>
      </article>
    </section>
  );
}
