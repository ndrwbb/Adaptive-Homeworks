import { useEffect } from "react";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";

export default function ProgressPage() {
  const { loadStudentProgress, loading, studentSnapshot } = useAppContext();

  useEffect(() => {
    loadStudentProgress();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading.student && !studentSnapshot.progress) {
    return <Loader label="Loading progress analytics..." />;
  }

  const progress = studentSnapshot.progress;
  if (!progress) {
    return null;
  }

  return (
    <section className="stack">
      <div className="hero-card hero-card--compact">
        <span className="eyebrow">Progress analytics</span>
        <h1>{progress.full_name}</h1>
        <p>
          The current learner model is baseline and rule-based, but already exposes measurable signals
          for progress tracking and teacher review.
        </p>
      </div>

      <div className="stats-grid">
        <MetricCard label="Skill Score" value={progress.skill_score} />
        <MetricCard label="Correct Attempts" value={progress.correct_attempts} />
        <MetricCard label="Accuracy" value={`${progress.accuracy}%`} />
      </div>

      <article className="panel">
        <div className="panel__header">
          <div>
            <span className="eyebrow">Performance curve</span>
            <h2>Baseline proficiency bar</h2>
          </div>
        </div>

        <div className="meter">
          <div className="meter__fill" style={{ width: `${progress.skill_score}%` }} />
        </div>

        <div className="submission-list">
          {progress.recent_submissions.map((submission) => (
            <article key={submission.submission_id} className="submission-row">
              <div>
                <strong>{submission.task_title}</strong>
                <p>{submission.topic}</p>
              </div>
              <div className="submission-row__meta">
                <span>{submission.is_correct ? "Correct" : "Review needed"}</span>
                <strong>
                  {submission.score_delta > 0 ? "+" : ""}
                  {submission.score_delta}
                </strong>
              </div>
            </article>
          ))}
        </div>
      </article>
    </section>
  );
}

function MetricCard({ label, value }) {
  return (
    <article className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>derived from tracked submissions</p>
    </article>
  );
}
