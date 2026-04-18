import { useEffect, useState } from "react";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";
import { buildTeacherHomeworkCards } from "../lib/homeworks";

const DIFFICULTY_LABELS = {
  easy: "Easy",
  medium: "Medium",
  hard: "Hard",
};

const blankRule = () => ({
  topic: "",
  difficulty_group: "easy",
  count: 1,
});

const initialForm = {
  title: "",
  subject: "Mathematics",
  description: "",
  deadline: "2099-03-10T18:00:00",
  assignee_ids: [],
  rules: [blankRule()],
};

export default function TeacherHomeworksPage() {
  const { generateHomework, loadTeacherHomeworks, loadTopics, loading, teacherSnapshot } = useAppContext();
  const [showComposer, setShowComposer] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [generating, setGenerating] = useState(false);
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    loadTeacherHomeworks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (showComposer) {
      loadTopics();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showComposer]);

  if (loading.teacher && teacherSnapshot.homeworks.length === 0) {
    return <Loader label="Loading teacher homeworks..." />;
  }

  const cards = buildTeacherHomeworkCards(teacherSnapshot.homeworks, teacherSnapshot.students);
  const topics = teacherSnapshot.topics || [];

  function updateRule(index, field, value) {
    setForm((current) => ({
      ...current,
      rules: current.rules.map((rule, ruleIndex) =>
        ruleIndex === index ? { ...rule, [field]: value } : rule,
      ),
    }));
  }

  function removeRule(index) {
    setForm((current) => ({
      ...current,
      rules: current.rules.filter((_, ruleIndex) => ruleIndex !== index),
    }));
  }

  async function handleGenerate(event) {
    event.preventDefault();
    setError("");
    setPreview(null);

    if (form.assignee_ids.length === 0) {
      setError("Choose at least one assignee.");
      return;
    }

    if (form.rules.length === 0) {
      setError("Add at least one generation rule.");
      return;
    }

    const invalidRule = form.rules.find((rule) => !rule.topic);
    if (invalidRule) {
      setError("All rules must have a topic selected.");
      return;
    }

    setGenerating(true);
    try {
      const payload = {
        title: form.title,
        subject: form.subject,
        description: form.description,
        deadline: form.deadline,
        student_ids: form.assignee_ids,
        rules: form.rules.map((rule) => ({
          topic: rule.topic,
          difficulty_group: rule.difficulty_group,
          count: rule.count,
        })),
      };

      const result = await generateHomework(payload);
      if (result) {
        setPreview(result);
        setForm(initialForm);
        setShowComposer(false);
      }
    } catch {
      setError("Generation failed. Check that the task bank has matching tasks.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <section className="stack">
      <div className="toolbar-row">
        <div>
          <span className="eyebrow">Teacher homeworks</span>
          <h1>Assigned homework builder</h1>
        </div>
        <button type="button" className="primary-button" onClick={() => { setShowComposer((current) => !current); setPreview(null); }}>
          {showComposer ? "Close composer" : "New Homework"}
        </button>
      </div>

      {showComposer ? (
        <form className="panel stack" onSubmit={handleGenerate}>
          <div className="field-grid">
            <label className="field">
              <span>Title</span>
              <input
                value={form.title}
                onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
                required
              />
            </label>
            <label className="field">
              <span>Subject</span>
              <input
                value={form.subject}
                onChange={(event) => setForm((current) => ({ ...current, subject: event.target.value }))}
                required
              />
            </label>
          </div>

          <label className="field">
            <span>Description</span>
            <textarea
              rows="4"
              value={form.description}
              onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
            />
          </label>

          <label className="field">
            <span>Deadline</span>
            <input
              type="datetime-local"
              value={form.deadline.slice(0, 16)}
              onChange={(event) =>
                setForm((current) => ({ ...current, deadline: `${event.target.value}:00` }))
              }
              required
            />
          </label>

          <div className="panel panel--subtle">
            <span className="eyebrow">Assignees</span>
            <div className="checkbox-grid">
              {teacherSnapshot.students.map((student) => (
                <label key={student.id} className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={form.assignee_ids.includes(student.id)}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        assignee_ids: event.target.checked
                          ? [...current.assignee_ids, student.id]
                          : current.assignee_ids.filter((id) => id !== student.id),
                      }))
                    }
                  />
                  <span>{student.full_name}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="stack">
            <div className="toolbar-row">
              <div>
                <span className="eyebrow">Generation rules</span>
                <h2>Configure auto-generation</h2>
              </div>
              <button
                type="button"
                className="ghost-button"
                onClick={() =>
                  setForm((current) => ({ ...current, rules: [...current.rules, blankRule()] }))
                }
              >
                + Add rule
              </button>
            </div>

            {form.rules.map((rule, index) => (
              <div className="rule-row" key={index}>
                <label className="field">
                  <span>Topic</span>
                  <select
                    value={rule.topic}
                    onChange={(event) => updateRule(index, "topic", event.target.value)}
                    required
                  >
                    <option value="">Select topic…</option>
                    {topics.map((t) => (
                      <option key={t} value={t}>
                        {t.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="field">
                  <span>Difficulty</span>
                  <select
                    value={rule.difficulty_group}
                    onChange={(event) => updateRule(index, "difficulty_group", event.target.value)}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </label>
                <label className="field">
                  <span>Count</span>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={rule.count}
                    onChange={(event) => updateRule(index, "count", Math.max(1, Number(event.target.value)))}
                  />
                </label>
                <button
                  type="button"
                  className="rule-delete"
                  title="Remove rule"
                  onClick={() => removeRule(index)}
                >
                  🗑
                </button>
              </div>
            ))}
          </div>

          {error ? <p className="form-error">{error}</p> : null}

          <button type="submit" className="primary-button" disabled={generating}>
            {generating ? "Generating…" : "Generate homework"}
          </button>
        </form>
      ) : null}

      {preview ? (
        <div className="panel stack">
          <div>
            <span className="eyebrow">Generated preview</span>
            <h2>{preview.title}</h2>
            <p className="muted-copy">
              {preview.tasks_preview.length} tasks selected · max score {preview.max_score} · assigned to {preview.assignment_count} student(s)
            </p>
          </div>
          <div className="preview-grid">
            {preview.tasks_preview.map((task) => (
              <article className="preview-card" key={task.id}>
                <h3>{task.title}</h3>
                <p>{task.body}</p>
                <div className="preview-card__meta">
                  <span className="tag tag--info">{task.topic.replace(/_/g, " ")}</span>
                  <span className="tag tag--muted">Difficulty {task.difficulty}</span>
                  <span className="tag tag--success">{task.task_type}</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      ) : null}

      <div className="homework-grid">
        {cards.map((homework) => (
          <article className="homework-card" key={homework.homework_id}>
            <div className="homework-card__header">
              <div>
                <span className="eyebrow">Homework</span>
                <h2>{homework.title}</h2>
              </div>
              <span className={`tag tag--${homework.requires_manual_review ? "warning" : "success"}`}>
                {homework.requires_manual_review ? "Manual review" : "Auto-graded"}
              </span>
            </div>
            <p>{homework.subject}</p>
            <ul className="meta-list">
              <li>Deadline: {new Date(homework.deadline).toLocaleString()}</li>
              <li>Assignees: {homework.assigneeCount}</li>
              <li>Items: {homework.items.length}</li>
              <li>Max score: {homework.max_score}</li>
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}
