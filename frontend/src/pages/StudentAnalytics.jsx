import { useDeferredValue, useEffect, useEffectEvent, useState } from "react";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";

export default function StudentAnalytics() {
  const { loadStudentAnalytics, loadTeacherDashboard, loading, teacherSnapshot } = useAppContext();
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);

  const onLoad = useEffectEvent(async () => {
    const overview = await loadTeacherDashboard();
    const firstStudent = overview?.students?.[0];
    if (firstStudent) {
      await loadStudentAnalytics(firstStudent.id);
    }
  });

  useEffect(() => {
    onLoad();
  }, [onLoad]);

  const normalizedQuery = deferredQuery.trim().toLowerCase();
  const filteredStudents = normalizedQuery
    ? teacherSnapshot.students.filter((student) =>
        `${student.full_name} ${student.email}`.toLowerCase().includes(normalizedQuery),
      )
    : teacherSnapshot.students;

  if (loading.teacher && teacherSnapshot.students.length === 0) {
    return <Loader label="Preparing student analytics..." />;
  }

  return (
    <section className="workspace-grid workspace-grid--analytics">
      <article className="panel">
        <div className="panel__header">
          <div>
            <span className="eyebrow">Search students</span>
            <h1>Analytics selector</h1>
          </div>
        </div>

        <label className="field">
          <span>Filter by name or email</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Alex Student"
          />
        </label>

        <div className="student-list">
          {filteredStudents.map((student) => (
            <button
              key={student.id}
              type="button"
              className={`student-list__item${
                teacherSnapshot.selectedStudentId === student.id ? " student-list__item--active" : ""
              }`}
              onClick={() => loadStudentAnalytics(student.id)}
            >
              <strong>{student.full_name}</strong>
              <span>{student.email}</span>
              <small>
                Skill {student.skill_score} · {student.total_attempts} attempts
              </small>
            </button>
          ))}
        </div>
      </article>

      <article className="panel">
        <div className="panel__header">
          <div>
            <span className="eyebrow">Selected profile</span>
            <h2>{teacherSnapshot.selectedStudentProgress?.full_name || "Choose a student"}</h2>
          </div>
        </div>

        {teacherSnapshot.selectedStudentProgress ? (
          <>
            <div className="stats-grid">
              <article className="stat-card">
                <span>Skill Score</span>
                <strong>{teacherSnapshot.selectedStudentProgress.skill_score}</strong>
                <p>current baseline estimate</p>
              </article>
              <article className="stat-card">
                <span>Accuracy</span>
                <strong>{teacherSnapshot.selectedStudentProgress.accuracy}%</strong>
                <p>tracked correct answers</p>
              </article>
              <article className="stat-card">
                <span>Attempts</span>
                <strong>{teacherSnapshot.selectedStudentProgress.total_attempts}</strong>
                <p>recorded submissions</p>
              </article>
            </div>

            <div className="submission-list">
              {teacherSnapshot.selectedStudentProgress.recent_submissions.map((submission) => (
                <article key={submission.submission_id} className="submission-row">
                  <div>
                    <strong>{submission.task_title}</strong>
                    <p>{submission.topic}</p>
                  </div>
                  <div className="submission-row__meta">
                    <span>{submission.is_correct ? "Correct" : "Needs revision"}</span>
                    <strong>
                      {submission.score_delta > 0 ? "+" : ""}
                      {submission.score_delta}
                    </strong>
                  </div>
                </article>
              ))}
            </div>
          </>
        ) : (
          <p className="muted-copy">Pick a student from the left panel to load recent analytics.</p>
        )}
      </article>
    </section>
  );
}
