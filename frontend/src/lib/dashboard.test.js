import test from "node:test";
import assert from "node:assert/strict";

import { buildStudentDashboardState } from "./dashboard.js";

test("builds dashboard state when recommendation is missing", () => {
  const state = buildStudentDashboardState({
    progress: {
      skill_score: 55,
      accuracy: 80,
      total_attempts: 5,
      recent_submissions: [],
    },
    homeworkSummary: [
      {
        assignment_id: 1,
        title: "Foundations Homework",
        deadline: "2099-03-05T18:00:00",
        status: "in_progress",
      },
    ],
    recommendation: null,
  });

  assert.equal(state.recommendation.status, "empty");
  assert.equal(state.homeworks.activeCount, 1);
});
