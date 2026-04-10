import { startTransition, useEffect, useState } from "react";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";

const initialForm = {
  title: "",
  body: "",
  difficulty: 2,
  topic: "algebra",
  answer_key: "",
};

export default function TaskManager() {
  const { createTask, loadTeacherDashboard, loading, teacherSnapshot } = useAppContext();
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");

  useEffect(() => {
    loadTeacherDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await createTask(form);
      startTransition(() => {
        setForm(initialForm);
      });
    } catch {
      setError("Task could not be created.");
    }
  }

  if (loading.teacher && teacherSnapshot.tasks.length === 0) {
    return <Loader label="Loading task bank..." />;
  }

  return (
    <section className="workspace-grid">
      <article className="panel">
        <div className="panel__header">
          <div>
            <span className="eyebrow">Task bank</span>
            <h1>Create reusable self-education content</h1>
          </div>
        </div>

        <form className="stack" onSubmit={handleSubmit}>
          <label className="field">
            <span>Title</span>
            <input
              value={form.title}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              placeholder="Quadratic practice"
              required
            />
          </label>

          <label className="field">
            <span>Prompt</span>
            <textarea
              rows="5"
              value={form.body}
              onChange={(event) => setForm((current) => ({ ...current, body: event.target.value }))}
              placeholder="Describe the task..."
              required
            />
          </label>

          <div className="field-grid">
            <label className="field">
              <span>Difficulty</span>
              <select
                value={form.difficulty}
                onChange={(event) => setForm((current) => ({ ...current, difficulty: Number(event.target.value) }))}
              >
                <option value={1}>Level 1</option>
                <option value={2}>Level 2</option>
                <option value={3}>Level 3</option>
              </select>
            </label>

            <label className="field">
              <span>Topic</span>
              <input
                value={form.topic}
                onChange={(event) => setForm((current) => ({ ...current, topic: event.target.value }))}
                placeholder="algebra"
              />
            </label>
          </div>

          <label className="field">
            <span>Answer key</span>
            <input
              value={form.answer_key}
              onChange={(event) => setForm((current) => ({ ...current, answer_key: event.target.value }))}
              placeholder="Optional for open-ended tasks"
            />
          </label>

          {error ? <p className="form-error">{error}</p> : null}

          <button type="submit" className="primary-button">
            Save to task bank
          </button>
        </form>
      </article>

      <article className="panel">
        <div className="panel__header">
          <div>
            <span className="eyebrow">Task library</span>
            <h2>Reusable practice tasks</h2>
          </div>
        </div>

        <div className="submission-list">
          {teacherSnapshot.tasks.map((task) => (
            <article key={task.id} className="submission-row">
              <div>
                <strong>{task.title}</strong>
                <p>{task.body}</p>
              </div>
              <div className="submission-row__meta">
                <span>{task.topic}</span>
                <strong>Level {task.difficulty}</strong>
              </div>
            </article>
          ))}
        </div>
      </article>
    </section>
  );
}
