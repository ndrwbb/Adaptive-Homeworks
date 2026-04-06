import { useEffect, useEffectEvent, useState } from "react";
import { useParams } from "react-router-dom";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";

export default function HomeworkDetailPage() {
  const { assignmentId } = useParams();
  const { evaluateHomeworkItem, loading, openHomeworkDetail, studentSnapshot } = useAppContext();
  const [answers, setAnswers] = useState({});
  const onLoad = useEffectEvent(() => {
    openHomeworkDetail(Number(assignmentId));
  });

  useEffect(() => {
    onLoad();
  }, [onLoad]);

  const homework = studentSnapshot.selectedHomework;
  if (loading.homework && !homework) {
    return <Loader label="Loading homework detail..." />;
  }

  if (!homework) {
    return null;
  }

  return (
    <section className="stack">
      <article className="panel panel--featured">
        <div className="panel__header">
          <div>
            <span className="eyebrow">Homework detail</span>
            <h1>{homework.title}</h1>
          </div>
          <span className="difficulty-badge">{homework.status.replaceAll("_", " ")}</span>
        </div>
        <p>{homework.description}</p>
        <div className="meta-list">
          <span>Teacher: {homework.teacher_name}</span>
          <span>Subject: {homework.subject}</span>
          <span>Deadline: {new Date(homework.deadline).toLocaleString()}</span>
          <span>
            Score:{" "}
            {homework.final_score != null
              ? `${homework.final_score}/${homework.max_score}`
              : `pending / ${homework.max_score}`}
          </span>
        </div>
      </article>

      <div className="stack">
        {homework.items.map((item) => (
          <article className="panel" key={item.id}>
            <div className="panel__header">
              <div>
                <span className="eyebrow">{item.item_type === "manual" ? "Manual review" : "Auto-graded"}</span>
                <h2>{item.title}</h2>
              </div>
              <span className="difficulty-badge">Level {item.difficulty}</span>
            </div>
            <p>{item.prompt}</p>
            <div className="panel__meta">
              <span>{item.max_points} points</span>
            </div>
            <div className="stack">
              <label className="field">
                <span>Your answer</span>
                <textarea
                  rows="4"
                  value={answers[item.id] || ""}
                  onChange={(event) =>
                    setAnswers((current) => ({ ...current, [item.id]: event.target.value }))
                  }
                />
              </label>
              <button
                type="button"
                className="primary-button"
                onClick={() => evaluateHomeworkItem(Number(assignmentId), item.id, answers[item.id] || "")}
              >
                Submit item
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
