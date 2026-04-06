import test from "node:test";
import assert from "node:assert/strict";

import { buildTeacherHomeworkCards, getHomeworkCardStatus } from "./homeworks.js";

test("computes homework card status after deadline", () => {
  const homework = {
    deadline: "2020-01-01T00:00:00",
    requires_manual_review: false,
    max_score: 10,
  };
  const assignment = {
    status: "not_started",
    final_score: null,
  };

  const status = getHomeworkCardStatus(homework, assignment);

  assert.equal(status.label, "Closed");
});

test("builds teacher homework summary cards", () => {
  const cards = buildTeacherHomeworkCards(
    [
      {
        homework_id: 1,
        title: "Algebra Homework",
        subject: "Mathematics",
        deadline: "2099-01-01T18:00:00",
        assignment_count: 2,
        requires_manual_review: true,
        max_score: 20,
        items: [],
      },
    ],
    [{ id: 1 }, { id: 2 }],
  );

  assert.equal(cards[0].assigneeCount, 2);
});
