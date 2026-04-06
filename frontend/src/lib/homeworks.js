function isPastDeadline(deadline) {
  return new Date(deadline).getTime() < Date.now();
}

export function getHomeworkCardStatus(homework, assignment) {
  const status = assignment?.status || "not_started";

  if (status === "checked") {
    return {
      key: "checked",
      label: "Checked",
      tone: "success",
      scoreLabel:
        assignment?.final_score != null
          ? `${assignment.final_score}/${homework.max_score}`
          : null,
    };
  }

  if (status === "on_review" || status === "submitted") {
    return { key: "on_review", label: "On review", tone: "warning", scoreLabel: null };
  }

  if (isPastDeadline(homework.deadline)) {
    return {
      key: "closed",
      label: "Closed",
      tone: "muted",
      scoreLabel:
        assignment?.final_score != null
          ? `${assignment.final_score}/${homework.max_score}`
          : null,
    };
  }

  if (status === "in_progress") {
    return { key: "in_progress", label: "In progress", tone: "info", scoreLabel: null };
  }

  return { key: "not_started", label: "Not started", tone: "muted", scoreLabel: null };
}

export function buildTeacherHomeworkCards(homeworks, students) {
  return homeworks.map((homework) => ({
    ...homework,
    assigneeCount: homework.assignment_count ?? students.length,
  }));
}
