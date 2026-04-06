import { useEffect, useEffectEvent, useState } from "react";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";
import { buildTeacherHomeworkCards } from "../lib/homeworks";

const blankItem = () => ({
  title: "",
  prompt: "",
  item_type: "test",
  difficulty: 1,
  max_points: 5,
  answer_key: "",
});

const initialForm = {
  title: "",
  subject: "Mathematics",
  description: "",
  deadline: "2099-03-10T18:00:00",
  assignee_ids: [],
  items: [blankItem()],
};

export default function TeacherHomeworksPage() {
  const { createHomework, loadTeacherHomeworks, loading, teacherSnapshot } = useAppContext();
  const [showComposer, setShowComposer] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const onLoad = useEffectEvent(() => {
    loadTeacherHomeworks();
  });

  useEffect(() => {
    onLoad();
  }, [onLoad]);

  if (loading.teacher && teacherSnapshot.homeworks.length === 0) {
    return <Loader label="Loading teacher homeworks..." />;
  }

  const cards = buildTeacherHomeworkCards(teacherSnapshot.homeworks, teacherSnapshot.students);

  function updateItem(index, field, value) {
    setForm((current) => ({
      ...current,
      items: current.items.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item,
      ),
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (form.assignee_ids.length === 0) {
      setError("Choose at least one assignee.");
      return;
    }

    await createHomework(form);
    setForm(initialForm);
    setShowComposer(false);
  }

  return (
    <section className="stack">
      <div className="toolbar-row">
        <div>
          <span className="eyebrow">Teacher homeworks</span>
          <h1>Assigned homework builder</h1>
        </div>
        <button type="button" className="primary-button" onClick={() => setShowComposer((current) => !current)}>
          {showComposer ? "Close composer" : "New Homework"}
        </button>
      </div>

      {showComposer ? (
        <form className="panel stack" onSubmit={handleSubmit}>
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
              required
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
                <span className="eyebrow">Homework items</span>
                <h2>Fill the assignment with exercises</h2>
              </div>
              <button
                type="button"
                className="ghost-button"
                onClick={() =>
                  setForm((current) => ({ ...current, items: [...current.items, blankItem()] }))
                }
              >
                Add item
              </button>
            </div>

            {form.items.map((item, index) => (
              <div className="panel panel--subtle stack" key={`${index}-${item.title}`}>
                <div className="field-grid">
                  <label className="field">
                    <span>Title</span>
                    <input value={item.title} onChange={(event) => updateItem(index, "title", event.target.value)} required />
                  </label>
                  <label className="field">
                    <span>Type</span>
                    <select
                      value={item.item_type}
                      onChange={(event) => updateItem(index, "item_type", event.target.value)}
                    >
                      <option value="test">Test</option>
                      <option value="manual">Manual</option>
                    </select>
                  </label>
                </div>
                <label className="field">
                  <span>Prompt</span>
                  <textarea rows="3" value={item.prompt} onChange={(event) => updateItem(index, "prompt", event.target.value)} required />
                </label>
                <div className="field-grid">
                  <label className="field">
                    <span>Difficulty</span>
                    <select
                      value={item.difficulty}
                      onChange={(event) => updateItem(index, "difficulty", Number(event.target.value))}
                    >
                      <option value={1}>Level 1</option>
                      <option value={2}>Level 2</option>
                      <option value={3}>Level 3</option>
                    </select>
                  </label>
                  <label className="field">
                    <span>Max points</span>
                    <input
                      type="number"
                      min="1"
                      value={item.max_points}
                      onChange={(event) => updateItem(index, "max_points", Number(event.target.value))}
                    />
                  </label>
                </div>
                {item.item_type === "test" ? (
                  <label className="field">
                    <span>Answer key</span>
                    <input
                      value={item.answer_key}
                      onChange={(event) => updateItem(index, "answer_key", event.target.value)}
                      required
                    />
                  </label>
                ) : null}
              </div>
            ))}
          </div>

          {error ? <p className="form-error">{error}</p> : null}

          <button type="submit" className="primary-button">
            Publish homework
          </button>
        </form>
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
