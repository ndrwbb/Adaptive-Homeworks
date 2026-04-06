import { getHomeworkCardStatus } from "../lib/homeworks.js";

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

const baseUsers = [
  {
    id: 1,
    email: "student@example.com",
    full_name: "Alex Student",
    role: "student",
    password: "demo123",
  },
  {
    id: 2,
    email: "teacher@example.com",
    full_name: "Maria Teacher",
    role: "teacher",
    password: "demo123",
  },
];

const baseTasks = [
  {
    id: 1,
    title: "Linear equation",
    body: "Solve the equation: 2x + 3 = 11",
    difficulty: 1,
    topic: "algebra",
    answer_key: "4",
  },
  {
    id: 2,
    title: "Fractions warm-up",
    body: "Compute: 3/4 + 1/4",
    difficulty: 1,
    topic: "arithmetic",
    answer_key: "1",
  },
  {
    id: 3,
    title: "System of equations",
    body: "Find x if x + y = 10 and y = 4.",
    difficulty: 2,
    topic: "algebra",
    answer_key: "6",
  },
  {
    id: 4,
    title: "Essay reflection",
    body: "Explain in 2-3 sentences why regular practice improves learning outcomes.",
    difficulty: 2,
    topic: "reflection",
    answer_key: null,
  },
  {
    id: 5,
    title: "Quadratic roots",
    body: "Find both roots of x^2 - 5x + 6 = 0.",
    difficulty: 3,
    topic: "algebra",
    answer_key: "2, 3",
  },
  {
    id: 6,
    title: "Derivative warm-up",
    body: "What is the derivative of x^2?",
    difficulty: 3,
    topic: "calculus",
    answer_key: "2x",
  },
];

const baseSubmissions = [
  {
    submission_id: 101,
    user_id: 1,
    task_id: 1,
    answer: "4",
    is_correct: true,
    score_delta: 5,
    submitted_at: "2026-03-01T09:00:00",
  },
  {
    submission_id: 102,
    user_id: 1,
    task_id: 3,
    answer: "5",
    is_correct: false,
    score_delta: -10,
    submitted_at: "2026-03-01T13:30:00",
  },
  {
    submission_id: 103,
    user_id: 1,
    task_id: 2,
    answer: "1",
    is_correct: true,
    score_delta: 5,
    submitted_at: "2026-03-02T10:15:00",
  },
];

const baseLearnerStates = {
  1: { skill_score: 58 },
};

const baseHomeworks = [
  {
    id: 1,
    title: "Foundations Homework",
    subject: "Mathematics",
    description: "Complete one test item and one explanation item.",
    teacher_id: 2,
    deadline: "2099-03-05T18:00:00",
    max_score: 10,
    requires_manual_review: true,
  },
  {
    id: 2,
    title: "Quick Algebra Check",
    subject: "Mathematics",
    description: "Short auto-graded algebra block.",
    teacher_id: 2,
    deadline: "2099-03-07T20:00:00",
    max_score: 8,
    requires_manual_review: false,
  },
];

const baseHomeworkItems = [
  {
    id: 1,
    homework_id: 1,
    title: "Equation drill",
    prompt: "Solve x + 5 = 12",
    item_type: "test",
    difficulty: 1,
    max_points: 5,
    answer_key: "7",
  },
  {
    id: 2,
    homework_id: 1,
    title: "Explain the approach",
    prompt: "Explain in words how you solved the equation.",
    item_type: "manual",
    difficulty: 1,
    max_points: 5,
    answer_key: null,
  },
  {
    id: 3,
    homework_id: 2,
    title: "Quadratic factorisation",
    prompt: "Find both roots of x^2 - 5x + 6 = 0",
    item_type: "test",
    difficulty: 2,
    max_points: 8,
    answer_key: "2, 3",
  },
];

const baseHomeworkAssignments = [
  {
    id: 1,
    homework_id: 1,
    student_id: 1,
    status: "in_progress",
    final_score: 5,
  },
  {
    id: 2,
    homework_id: 2,
    student_id: 1,
    status: "not_started",
    final_score: null,
  },
];

const baseHomeworkSubmissions = [
  {
    id: 1,
    assignment_id: 1,
    item_id: 1,
    answer: "7",
    is_correct: true,
    awarded_points: 5,
    review_status: "reviewed",
    submitted_at: "2026-03-02T12:20:00",
  },
];

function normalizeAnswer(answer) {
  return answer.trim().toLowerCase().replace(/\s+/g, " ");
}

function pickDifficulty(skillScore) {
  if (skillScore < 40) return 1;
  if (skillScore < 70) return 2;
  return 3;
}

function getTaskById(state, taskId) {
  return state.tasks.find((task) => task.id === taskId);
}

function getUserById(state, userId) {
  return state.users.find((user) => user.id === userId);
}

function getHomeworkById(state, homeworkId) {
  return state.homeworks.find((homework) => homework.id === homeworkId);
}

function getAssignmentById(state, assignmentId) {
  return state.homeworkAssignments.find((assignment) => assignment.id === assignmentId);
}

function getHomeworkItems(state, homeworkId) {
  return state.homeworkItems.filter((item) => item.homework_id === homeworkId);
}

function getHomeworkSubmissions(state, assignmentId) {
  return state.homeworkSubmissions.filter((submission) => submission.assignment_id === assignmentId);
}

function computeAssignmentState(state, assignment) {
  const homework = getHomeworkById(state, assignment.homework_id);
  const items = getHomeworkItems(state, homework.id);
  const submissions = getHomeworkSubmissions(state, assignment.id);
  const manualPending = items.some((item) => {
    const submission = submissions.find((current) => current.item_id === item.id);
    return item.item_type === "manual" && submission && submission.review_status !== "reviewed";
  });
  const score = submissions.reduce((total, submission) => total + submission.awarded_points, 0);

  let status = "not_started";
  if (manualPending) {
    status = "on_review";
  } else if (submissions.length === 0) {
    status = "not_started";
  } else if (submissions.length < items.length) {
    status = "in_progress";
  } else {
    status = "checked";
  }

  return {
    ...assignment,
    status,
    final_score: submissions.length ? score : assignment.final_score,
  };
}

function buildHomeworkSummary(state, assignment) {
  const computedAssignment = computeAssignmentState(state, assignment);
  const homework = getHomeworkById(state, assignment.homework_id);
  const teacher = getUserById(state, homework.teacher_id);
  const items = getHomeworkItems(state, homework.id);
  const submissions = getHomeworkSubmissions(state, assignment.id);
  const statusInfo = getHomeworkCardStatus(homework, computedAssignment);
  return {
    assignment_id: assignment.id,
    homework_id: homework.id,
    title: homework.title,
    subject: homework.subject,
    teacher_name: teacher?.full_name || "Teacher",
    deadline: homework.deadline,
    progress_label: `${submissions.length}/${items.length} items completed`,
    status: statusInfo.key,
    status_label: statusInfo.label,
    final_score: computedAssignment.final_score,
    max_score: homework.max_score,
    requires_manual_review: homework.requires_manual_review,
  };
}

export function createDemoState() {
  return {
    users: clone(baseUsers),
    tasks: clone(baseTasks),
    submissions: clone(baseSubmissions),
    learnerStates: clone(baseLearnerStates),
    homeworks: clone(baseHomeworks),
    homeworkItems: clone(baseHomeworkItems),
    homeworkAssignments: clone(baseHomeworkAssignments),
    homeworkSubmissions: clone(baseHomeworkSubmissions),
    nextTaskId: 7,
    nextSubmissionId: 104,
    nextUserId: 3,
    nextHomeworkId: 3,
    nextHomeworkItemId: 4,
    nextHomeworkAssignmentId: 3,
    nextHomeworkSubmissionId: 2,
  };
}

export function cloneDemoState(state) {
  return clone(state);
}

export function findDemoUser(state, email, password) {
  return state.users.find(
    (user) => user.email.toLowerCase() === email.toLowerCase() && user.password === password,
  );
}

export function registerDemoUser(state, payload) {
  const existing = state.users.find(
    (user) => user.email.toLowerCase() === payload.email.toLowerCase(),
  );
  if (existing) {
    throw new Error("Email already registered in demo mode.");
  }

  const user = {
    id: state.nextUserId,
    email: payload.email.toLowerCase(),
    full_name: payload.full_name.trim(),
    role: payload.role,
    password: payload.password,
  };
  state.nextUserId += 1;
  state.users.push(user);

  if (user.role === "student") {
    state.learnerStates[user.id] = { skill_score: 50 };
  }

  return user;
}

export function getPracticeOptions(state) {
  return {
    topics: [...new Set(state.tasks.map((task) => task.topic))].sort(),
    difficulties: [1, 2, 3],
  };
}

export function getDemoRecommendation(state, studentId, filters = {}) {
  const learnerState = state.learnerStates[studentId] || { skill_score: 50 };
  const difficulty = filters.difficulty ?? pickDifficulty(learnerState.skill_score);
  const topic = filters.topic;
  const filtered = state.tasks.filter(
    (task) =>
      (difficulty ? task.difficulty === Number(difficulty) : true) &&
      (topic ? task.topic === topic : true),
  );
  return filtered[0] || state.tasks[0] || null;
}

export function getDemoProgress(state, studentId) {
  const user = getUserById(state, studentId);
  const learnerState = state.learnerStates[studentId] || { skill_score: 50 };
  const submissions = state.submissions
    .filter((submission) => submission.user_id === studentId)
    .sort((left, right) => right.submitted_at.localeCompare(left.submitted_at));

  const totalAttempts = submissions.length;
  const correctAttempts = submissions.filter((submission) => submission.is_correct).length;
  const accuracy = totalAttempts ? Number(((correctAttempts / totalAttempts) * 100).toFixed(2)) : 0;

  return {
    user_id: studentId,
    full_name: user?.full_name || "Demo Student",
    skill_score: learnerState.skill_score,
    total_attempts: totalAttempts,
    correct_attempts: correctAttempts,
    accuracy,
    recent_submissions: submissions.slice(0, 5).map((submission) => {
      const task = getTaskById(state, submission.task_id);
      return {
        submission_id: submission.submission_id,
        task_title: task?.title || "Task",
        topic: task?.topic || "general",
        is_correct: submission.is_correct,
        score_delta: submission.score_delta,
        submitted_at: submission.submitted_at,
      };
    }),
  };
}

export function listDemoHomeworks(state, studentId) {
  return state.homeworkAssignments
    .filter((assignment) => assignment.student_id === studentId)
    .map((assignment) => buildHomeworkSummary(state, assignment));
}

export function getDemoHomeworkDetail(state, studentId, assignmentId) {
  const assignment = state.homeworkAssignments.find(
    (current) => current.id === Number(assignmentId) && current.student_id === studentId,
  );
  if (!assignment) {
    throw new Error("Homework assignment not found.");
  }

  const computedAssignment = computeAssignmentState(state, assignment);
  const homework = getHomeworkById(state, assignment.homework_id);
  const teacher = getUserById(state, homework.teacher_id);
  const items = getHomeworkItems(state, homework.id);

  return {
    assignment_id: assignment.id,
    homework_id: homework.id,
    title: homework.title,
    subject: homework.subject,
    description: homework.description,
    teacher_name: teacher?.full_name || "Teacher",
    deadline: homework.deadline,
    status: computedAssignment.status,
    final_score: computedAssignment.final_score,
    max_score: homework.max_score,
    requires_manual_review: homework.requires_manual_review,
    items,
  };
}

export function getDemoStudentSummaries(state) {
  return state.users
    .filter((user) => user.role === "student")
    .map((user) => {
      const progress = getDemoProgress(state, user.id);
      return {
        id: user.id,
        email: user.email,
        full_name: user.full_name,
        role: user.role,
        skill_score: progress.skill_score,
        total_attempts: progress.total_attempts,
      };
    });
}

export function submitDemoAnswer(state, studentId, taskId, answer) {
  const task = getTaskById(state, taskId);
  if (!task) {
    throw new Error("Task not found in demo mode.");
  }

  const learnerState = state.learnerStates[studentId] || { skill_score: 50 };
  const hasAnswerKey = Boolean(task.answer_key);
  const isCorrect = hasAnswerKey
    ? normalizeAnswer(answer) === normalizeAnswer(task.answer_key)
    : answer.trim().length > 10;
  const delta = (isCorrect ? 1 : -1) * 5 * task.difficulty;

  learnerState.skill_score = Math.max(0, Math.min(100, learnerState.skill_score + delta));
  state.learnerStates[studentId] = learnerState;

  const submission = {
    submission_id: state.nextSubmissionId,
    user_id: studentId,
    task_id: taskId,
    answer,
    is_correct: isCorrect,
    score_delta: delta,
    submitted_at: new Date().toISOString(),
  };
  state.nextSubmissionId += 1;
  state.submissions.push(submission);

  return {
    submission_id: submission.submission_id,
    new_skill_score: learnerState.skill_score,
    delta,
    is_correct: isCorrect,
    message: isCorrect
      ? "Correct answer. Demo profile updated."
      : "Answer recorded. Demo profile adjusted.",
  };
}

export function submitDemoHomeworkItem(state, studentId, assignmentId, itemId, answer) {
  const assignment = state.homeworkAssignments.find(
    (current) => current.id === Number(assignmentId) && current.student_id === studentId,
  );
  const item = state.homeworkItems.find((current) => current.id === Number(itemId));
  if (!assignment || !item) {
    throw new Error("Homework submission target not found.");
  }

  const existing = state.homeworkSubmissions.find(
    (current) => current.assignment_id === assignment.id && current.item_id === item.id,
  );
  const isCorrect =
    item.item_type === "test"
      ? normalizeAnswer(answer) === normalizeAnswer(item.answer_key || "")
      : null;
  const awardedPoints = item.item_type === "test" ? (isCorrect ? item.max_points : 0) : 0;
  const reviewStatus = item.item_type === "test" ? "reviewed" : "pending";

  if (existing) {
    existing.answer = answer;
    existing.is_correct = isCorrect;
    existing.awarded_points = awardedPoints;
    existing.review_status = reviewStatus;
  } else {
    state.homeworkSubmissions.push({
      id: state.nextHomeworkSubmissionId,
      assignment_id: assignment.id,
      item_id: item.id,
      answer,
      is_correct: isCorrect,
      awarded_points: awardedPoints,
      review_status: reviewStatus,
      submitted_at: new Date().toISOString(),
    });
    state.nextHomeworkSubmissionId += 1;
  }

  const computed = computeAssignmentState(state, assignment);
  assignment.status = computed.status;
  assignment.final_score = computed.final_score;

  return {
    submission_id: state.nextHomeworkSubmissionId - 1,
    review_status: reviewStatus,
    is_correct: isCorrect,
    awarded_points: awardedPoints,
    status: computed.status,
  };
}

export function getDemoTeacherHomeworks(state, teacherId) {
  return state.homeworks
    .filter((homework) => homework.teacher_id === teacherId)
    .map((homework) => ({
      homework_id: homework.id,
      title: homework.title,
      subject: homework.subject,
      deadline: homework.deadline,
      assignment_count: state.homeworkAssignments.filter(
        (assignment) => assignment.homework_id === homework.id,
      ).length,
      requires_manual_review: homework.requires_manual_review,
      max_score: homework.max_score,
      items: getHomeworkItems(state, homework.id),
    }));
}

export function createDemoTask(state, payload) {
  const task = {
    id: state.nextTaskId,
    title: payload.title.trim(),
    body: payload.body.trim(),
    difficulty: Number(payload.difficulty),
    topic: payload.topic.trim(),
    answer_key: payload.answer_key?.trim() || null,
  };
  state.nextTaskId += 1;
  state.tasks.push(task);
  return task;
}

export function createDemoHomework(state, teacherId, payload) {
  const homework = {
    id: state.nextHomeworkId,
    title: payload.title.trim(),
    subject: payload.subject.trim(),
    description: payload.description.trim(),
    teacher_id: teacherId,
    deadline: payload.deadline,
    max_score: payload.items.reduce((sum, item) => sum + Number(item.max_points), 0),
    requires_manual_review: payload.items.some((item) => item.item_type === "manual"),
  };
  state.nextHomeworkId += 1;
  state.homeworks.push(homework);

  const createdItems = payload.items.map((item) => {
    const nextItem = {
      id: state.nextHomeworkItemId,
      homework_id: homework.id,
      title: item.title.trim(),
      prompt: item.prompt.trim(),
      item_type: item.item_type,
      difficulty: Number(item.difficulty),
      max_points: Number(item.max_points),
      answer_key: item.answer_key?.trim() || null,
    };
    state.nextHomeworkItemId += 1;
    state.homeworkItems.push(nextItem);
    return nextItem;
  });

  payload.assignee_ids.forEach((studentId) => {
    state.homeworkAssignments.push({
      id: state.nextHomeworkAssignmentId,
      homework_id: homework.id,
      student_id: Number(studentId),
      status: "not_started",
      final_score: null,
    });
    state.nextHomeworkAssignmentId += 1;
  });

  return {
    homework_id: homework.id,
    title: homework.title,
    subject: homework.subject,
    deadline: homework.deadline,
    assignment_count: payload.assignee_ids.length,
    requires_manual_review: homework.requires_manual_review,
    max_score: homework.max_score,
    items: createdItems,
  };
}
