import { useEffect, useEffectEvent, useState } from "react";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";

export default function SelfEducationPage() {
  const { evaluatePracticeSubmission, loadPracticeTask, loading, studentSnapshot } = useAppContext();
  const [answer, setAnswer] = useState("");
  const [filters, setFilters] = useState(studentSnapshot.practiceFilters);
  const onLoad = useEffectEvent(() => {
    loadPracticeTask(studentSnapshot.practiceFilters, { quiet: true });
  });

  useEffect(() => {
    if (!studentSnapshot.practiceTask) {
      onLoad();
    }
  }, [onLoad, studentSnapshot.practiceTask]);

  const options = studentSnapshot.practiceOptions;
  const task = studentSnapshot.practiceTask;

  async function handleStart(event) {
    event.preventDefault();
    await loadPracticeTask(filters);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!task) {
      return;
    }
    await evaluatePracticeSubmission(task.id, answer);
    setAnswer("");
  }

  return (
    <section className="stack">
      <div className="hero-card hero-card--compact">
        <span className="eyebrow">Self-Education mode</span>
        <h1>Choose subject and difficulty, then practice freely.</h1>
        <p>Self-education is auto-graded and does not require teacher review.</p>
      </div>

      <form className="panel filter-panel" onSubmit={handleStart}>
        <div className="field-grid">
          <label className="field">
            <span>Subject</span>
            <select
              value={filters.topic}
              onChange={(event) => setFilters((current) => ({ ...current, topic: event.target.value }))}
            >
              {options.topics.map((topic) => (
                <option key={topic} value={topic}>
                  {topic}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Difficulty</span>
            <select
              value={filters.difficulty}
              onChange={(event) =>
                setFilters((current) => ({ ...current, difficulty: Number(event.target.value) }))
              }
            >
              {options.difficulties.map((difficulty) => (
                <option key={difficulty} value={difficulty}>
                  Level {difficulty}
                </option>
              ))}
            </select>
          </label>
        </div>

        <button type="submit" className="primary-button">
          Start practice
        </button>
      </form>

      {loading.practice && !task ? <Loader label="Preparing self-education task..." /> : null}

      {task ? (
        <section className="workspace-grid">
          <article className="panel panel--featured">
            <div className="panel__header">
              <div>
                <span className="eyebrow">Practice task</span>
                <h2>{task.title}</h2>
              </div>
              <span className="difficulty-badge">Level {task.difficulty}</span>
            </div>
            <p>{task.body}</p>
            <div className="panel__meta">
              <span>{task.topic}</span>
            </div>
          </article>

          <article className="panel">
            <div className="panel__header">
              <div>
                <span className="eyebrow">Answer submission</span>
                <h2>Send your response</h2>
              </div>
            </div>
            <form className="stack" onSubmit={handleSubmit}>
              <label className="field">
                <span>Your answer</span>
                <textarea rows="5" value={answer} onChange={(event) => setAnswer(event.target.value)} />
              </label>
              <button type="submit" className="primary-button" disabled={loading.practice}>
                {loading.practice ? "Submitting..." : "Submit answer"}
              </button>
            </form>

            {studentSnapshot.lastPracticeSubmission ? (
              <div className="feedback-box">
                <strong>
                  {studentSnapshot.lastPracticeSubmission.is_correct ? "Correct attempt" : "Attempt saved"}
                </strong>
                <p>{studentSnapshot.lastPracticeSubmission.message}</p>
              </div>
            ) : null}
          </article>
        </section>
      ) : null}
    </section>
  );
}
