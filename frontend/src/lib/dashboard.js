export function buildStudentDashboardState({ progress, homeworkSummary, recommendation }) {
  const activeHomeworks = homeworkSummary.filter((homework) =>
    ["not_started", "in_progress", "submitted", "on_review"].includes(homework.status),
  );

  const nearestDeadline = [...homeworkSummary]
    .sort((left, right) => new Date(left.deadline).getTime() - new Date(right.deadline).getTime())[0] || null;

  return {
    overview: [
      { label: "Skill Score", value: progress?.skill_score ?? 0, note: "adaptive baseline" },
      { label: "Accuracy", value: `${progress?.accuracy ?? 0}%`, note: "tracked correctness" },
      { label: "Active Homeworks", value: activeHomeworks.length, note: "assigned by teachers" },
    ],
    homeworks: {
      activeCount: activeHomeworks.length,
      nearestDeadline,
      cards: homeworkSummary,
    },
    recommendation: recommendation
      ? { status: "ready", task: recommendation }
      : { status: "empty", task: null },
    recentSubmissions: progress?.recent_submissions ?? [],
  };
}
