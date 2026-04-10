import { useEffect } from "react";
import { Link } from "react-router-dom";

import Loader from "../components/Loader";
import { useAppContext } from "../context/AppContext";
import { getHomeworkCardStatus } from "../lib/homeworks";

export default function HomeworksPage() {
  const { loadStudentHomeworks, loading, studentSnapshot } = useAppContext();
  useEffect(() => {
    loadStudentHomeworks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading.homework && studentSnapshot.homeworks.length === 0) {
    return <Loader label="Loading homeworks..." />;
  }

  return (
    <section className="stack">
      <div className="hero-card hero-card--compact">
        <span className="eyebrow">Homework mode</span>
        <h1>Assigned homeworks</h1>
        <p>
          Each card represents a teacher-assigned homework with its own deadline, status, and score.
        </p>
      </div>

      <div className="homework-grid">
        {studentSnapshot.homeworks.map((homework) => {
          const status = getHomeworkCardStatus(
            {
              deadline: homework.deadline,
              requires_manual_review: homework.requires_manual_review,
              max_score: homework.max_score,
            },
            { status: homework.status, final_score: homework.final_score },
          );

          return (
            <Link
              key={homework.assignment_id}
              className="homework-card"
              to={`/student/homeworks/${homework.assignment_id}`}
            >
              <div className="homework-card__header">
                <div>
                  <span className="eyebrow">Homework</span>
                  <h2>{homework.title}</h2>
                </div>
                <span className={`tag tag--${status.tone}`}>{status.label}</span>
              </div>
              <p>{homework.subject}</p>
              <ul className="meta-list">
                <li>Teacher: {homework.teacher_name}</li>
                <li>Deadline: {new Date(homework.deadline).toLocaleString()}</li>
                <li>{homework.progress_label}</li>
                <li>
                  Score:{" "}
                  {homework.final_score != null
                    ? `${homework.final_score}/${homework.max_score}`
                    : `pending / ${homework.max_score}`}
                </li>
              </ul>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
