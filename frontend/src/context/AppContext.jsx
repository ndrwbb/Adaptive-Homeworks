import { createContext, startTransition, useContext, useEffect, useState } from "react";

import {
  createTeacherHomework,
  createTeacherTask,
  fetchHomeworkDetail,
  fetchMe,
  fetchMyHomeworks,
  fetchMyProgress,
  fetchRecommendation,
  fetchTeacherHomeworks,
  fetchTeacherStudentProgress,
  fetchTeacherStudents,
  fetchTeacherTasks,
  healthCheck,
  loginUser,
  registerUser,
  submitAnswer,
  submitHomeworkItem,
} from "../api/client";
import {
  cloneDemoState,
  createDemoHomework,
  createDemoState,
  createDemoTask,
  findDemoUser,
  getDemoHomeworkDetail,
  getDemoProgress,
  getDemoRecommendation,
  getDemoStudentSummaries,
  getDemoTeacherHomeworks,
  getPracticeOptions,
  listDemoHomeworks,
  registerDemoUser,
  submitDemoAnswer,
  submitDemoHomeworkItem,
} from "../api/demoData";
import { buildStudentDashboardState } from "../lib/dashboard";

const AppContext = createContext(null);
const SESSION_KEY = "adaptive-homework-session";
const defaultPracticeFilters = { topic: "algebra", difficulty: 2 };

const emptyStudentSnapshot = {
  progress: null,
  homeworks: [],
  selectedHomework: null,
  practiceTask: null,
  practiceFilters: defaultPracticeFilters,
  practiceOptions: { topics: [], difficulties: [1, 2, 3] },
  lastPracticeSubmission: null,
  lastHomeworkSubmission: null,
  dashboard: null,
};

const emptyTeacherSnapshot = {
  students: [],
  tasks: [],
  homeworks: [],
  stats: [],
  selectedStudentId: null,
  selectedStudentProgress: null,
};

function loadSession() {
  const raw = window.localStorage.getItem(SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}

function persistSession(session) {
  if (!session) {
    window.localStorage.removeItem(SESSION_KEY);
    return;
  }
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

function buildTeacherOverview(students, tasks, homeworks) {
  const pendingReview = homeworks.filter((homework) => homework.requires_manual_review).length;
  return {
    students,
    tasks,
    homeworks,
    stats: [
      { label: "Students", value: students.length, note: "available assignees" },
      { label: "Homeworks", value: homeworks.length, note: "teacher-created assignments" },
      { label: "Pending Review", value: pendingReview, note: "manual-review homeworks" },
      { label: "Task Bank", value: tasks.length, note: "reusable self-education content" },
    ],
  };
}

export function AppProvider({ children }) {
  const [session, setSession] = useState(() => loadSession());
  const [backendMode, setBackendMode] = useState("checking");
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState({
    auth: false,
    student: false,
    practice: false,
    homework: false,
    teacher: false,
  });
  const [studentSnapshot, setStudentSnapshot] = useState({
    ...emptyStudentSnapshot,
    practiceOptions: getPracticeOptions(createDemoState()),
  });
  const [teacherSnapshot, setTeacherSnapshot] = useState(emptyTeacherSnapshot);
  const [demoState, setDemoState] = useState(() => createDemoState());

  useEffect(() => {
    persistSession(session);
  }, [session]);

  useEffect(() => {
    let cancelled = false;

    async function probeBackend() {
      try {
        await healthCheck();
        if (!cancelled) {
          setBackendMode("live");
        }
      } catch {
        if (!cancelled) {
          setBackendMode("demo");
        }
      }
    }

    probeBackend();
    return () => {
      cancelled = true;
    };
  }, []);

  function pushToast(message, tone = "info") {
    setToast({ id: Date.now(), message, tone });
  }

  function clearToast() {
    setToast(null);
  }

  function updateDemo(mutator) {
    let result;
    let nextState;
    setDemoState((current) => {
      const next = cloneDemoState(current);
      nextState = next;
      result = mutator(next);
      return next;
    });
    return { nextState, result };
  }

  function resetSnapshots() {
    setStudentSnapshot({
      ...emptyStudentSnapshot,
      practiceOptions: getPracticeOptions(demoState),
    });
    setTeacherSnapshot(emptyTeacherSnapshot);
  }

  async function login(form) {
    setLoading((current) => ({ ...current, auth: true }));
    try {
      try {
        const liveSession = await loginUser(form.email, form.password);
        const resolvedUser = liveSession.user || (await fetchMe(liveSession.access_token));
        const nextSession = {
          token: liveSession.access_token,
          mode: "live",
          user: resolvedUser,
        };
        setSession(nextSession);
        setBackendMode("live");
        pushToast("Connected to live API.", "success");
        return nextSession;
      } catch (error) {
        const demoUser = findDemoUser(demoState, form.email, form.password);
        if (!demoUser) {
          throw error;
        }
        const nextSession = {
          token: "demo-token",
          mode: "demo",
          user: demoUser,
        };
        setSession(nextSession);
        setBackendMode("demo");
        pushToast("API unavailable. Switched to demo mode.", "warning");
        return nextSession;
      }
    } finally {
      setLoading((current) => ({ ...current, auth: false }));
    }
  }

  async function register(form) {
    setLoading((current) => ({ ...current, auth: true }));
    try {
      try {
        await registerUser(form);
        return login({ email: form.email, password: form.password });
      } catch {
        const { result: demoUser, nextState } = updateDemo((state) => registerDemoUser(state, form));
        const nextSession = {
          token: "demo-token",
          mode: "demo",
          user: demoUser,
        };
        setSession(nextSession);
        setBackendMode("demo");
        setStudentSnapshot((current) => ({
          ...current,
          practiceOptions: getPracticeOptions(nextState),
        }));
        pushToast("Registered in demo mode.", "success");
        return nextSession;
      }
    } finally {
      setLoading((current) => ({ ...current, auth: false }));
    }
  }

  function logout() {
    setSession(null);
    resetSnapshots();
    pushToast("Session closed.", "info");
  }

  async function loadPracticeTask(filters = studentSnapshot.practiceFilters, options = {}) {
    if (!session || session.user.role !== "student") {
      return null;
    }

    const { quiet = false } = options;
    if (!quiet) {
      setLoading((current) => ({ ...current, practice: true }));
    }

    try {
      if (session.mode === "live") {
        try {
          const task = await fetchRecommendation(session.token, filters);
          setStudentSnapshot((current) => ({
            ...current,
            practiceTask: task,
            practiceFilters: filters,
          }));
          setBackendMode("live");
          return task;
        } catch {
          setBackendMode("demo");
        }
      }

      const task = getDemoRecommendation(demoState, session.user.id, filters);
      setStudentSnapshot((current) => ({
        ...current,
        practiceTask: task,
        practiceFilters: filters,
        practiceOptions: getPracticeOptions(demoState),
      }));
      return task;
    } finally {
      if (!quiet) {
        setLoading((current) => ({ ...current, practice: false }));
      }
    }
  }

  async function loadStudentDashboard() {
    if (!session || session.user.role !== "student") {
      return null;
    }

    setLoading((current) => ({ ...current, student: true }));
    try {
      let progress;
      let homeworks;
      let usedDemo = session.mode !== "live";

      if (session.mode === "live") {
        const [progressResult, homeworksResult] = await Promise.allSettled([
          fetchMyProgress(session.token),
          fetchMyHomeworks(session.token),
        ]);

        if (progressResult.status === "fulfilled") {
          progress = progressResult.value;
        } else {
          progress = getDemoProgress(demoState, session.user.id);
          usedDemo = true;
        }

        if (homeworksResult.status === "fulfilled") {
          homeworks = homeworksResult.value;
        } else {
          homeworks = listDemoHomeworks(demoState, session.user.id);
          usedDemo = true;
        }
      } else {
        progress = getDemoProgress(demoState, session.user.id);
        homeworks = listDemoHomeworks(demoState, session.user.id);
      }

      const dashboard = buildStudentDashboardState({
        progress,
        homeworkSummary: homeworks,
        recommendation: studentSnapshot.practiceTask,
      });

      startTransition(() => {
        setStudentSnapshot((current) => ({
          ...current,
          progress,
          homeworks,
          dashboard,
          practiceOptions: getPracticeOptions(demoState),
        }));
      });

      setBackendMode(usedDemo ? "demo" : "live");
      void loadPracticeTask(studentSnapshot.practiceFilters, { quiet: true });
      return { progress, homeworks, dashboard };
    } finally {
      setLoading((current) => ({ ...current, student: false }));
    }
  }

  async function loadStudentProgress() {
    const result = await loadStudentDashboard();
    return result?.progress || null;
  }

  async function loadStudentHomeworks() {
    if (!session || session.user.role !== "student") {
      return [];
    }
    setLoading((current) => ({ ...current, homework: true }));
    try {
      if (session.mode === "live") {
        try {
          const homeworks = await fetchMyHomeworks(session.token);
          setStudentSnapshot((current) => ({ ...current, homeworks }));
          setBackendMode("live");
          return homeworks;
        } catch {
          setBackendMode("demo");
        }
      }

      const homeworks = listDemoHomeworks(demoState, session.user.id);
      setStudentSnapshot((current) => ({ ...current, homeworks }));
      return homeworks;
    } finally {
      setLoading((current) => ({ ...current, homework: false }));
    }
  }

  async function openHomeworkDetail(assignmentId) {
    if (!session || session.user.role !== "student") {
      return null;
    }
    setLoading((current) => ({ ...current, homework: true }));
    try {
      if (session.mode === "live") {
        try {
          const detail = await fetchHomeworkDetail(session.token, assignmentId);
          setStudentSnapshot((current) => ({ ...current, selectedHomework: detail }));
          setBackendMode("live");
          return detail;
        } catch {
          setBackendMode("demo");
        }
      }

      const detail = getDemoHomeworkDetail(demoState, session.user.id, assignmentId);
      setStudentSnapshot((current) => ({ ...current, selectedHomework: detail }));
      return detail;
    } finally {
      setLoading((current) => ({ ...current, homework: false }));
    }
  }

  async function evaluatePracticeSubmission(taskId, answer) {
    if (!session || session.user.role !== "student") {
      return null;
    }

    setLoading((current) => ({ ...current, practice: true }));
    try {
      if (session.mode === "live") {
        try {
          const result = await submitAnswer(session.token, { task_id: taskId, answer });
          const [progress, nextTask] = await Promise.all([
            fetchMyProgress(session.token),
            fetchRecommendation(session.token, studentSnapshot.practiceFilters),
          ]);
          startTransition(() => {
            setStudentSnapshot((current) => ({
              ...current,
              progress,
              practiceTask: nextTask,
              lastPracticeSubmission: result,
              dashboard: buildStudentDashboardState({
                progress,
                homeworkSummary: current.homeworks,
                recommendation: nextTask,
              }),
            }));
          });
          pushToast(result.message, result.is_correct ? "success" : "warning");
          setBackendMode("live");
          return result;
        } catch {
          setBackendMode("demo");
        }
      }

      const { nextState, result } = updateDemo((state) =>
        submitDemoAnswer(state, session.user.id, taskId, answer),
      );
      const progress = getDemoProgress(nextState, session.user.id);
      const task = getDemoRecommendation(nextState, session.user.id, studentSnapshot.practiceFilters);
      startTransition(() => {
        setStudentSnapshot((current) => ({
          ...current,
          progress,
          practiceTask: task,
          lastPracticeSubmission: result,
          practiceOptions: getPracticeOptions(nextState),
          dashboard: buildStudentDashboardState({
            progress,
            homeworkSummary: current.homeworks,
            recommendation: task,
          }),
        }));
      });
      pushToast(result.message, result.is_correct ? "success" : "warning");
      return result;
    } finally {
      setLoading((current) => ({ ...current, practice: false }));
    }
  }

  async function evaluateHomeworkItem(assignmentId, itemId, answer) {
    if (!session || session.user.role !== "student") {
      return null;
    }

    setLoading((current) => ({ ...current, homework: true }));
    try {
      if (session.mode === "live") {
        try {
          const result = await submitHomeworkItem(session.token, assignmentId, { item_id: itemId, answer });
          const [detail, homeworks, progress] = await Promise.all([
            fetchHomeworkDetail(session.token, assignmentId),
            fetchMyHomeworks(session.token),
            fetchMyProgress(session.token),
          ]);
          startTransition(() => {
            setStudentSnapshot((current) => ({
              ...current,
              selectedHomework: detail,
              homeworks,
              progress,
              lastHomeworkSubmission: result,
              dashboard: buildStudentDashboardState({
                progress,
                homeworkSummary: homeworks,
                recommendation: current.practiceTask,
              }),
            }));
          });
          pushToast("Homework item saved.", result.review_status === "reviewed" ? "success" : "warning");
          setBackendMode("live");
          return result;
        } catch {
          setBackendMode("demo");
        }
      }

      const { nextState, result } = updateDemo((state) =>
        submitDemoHomeworkItem(state, session.user.id, assignmentId, itemId, answer),
      );
      const detail = getDemoHomeworkDetail(nextState, session.user.id, assignmentId);
      const homeworks = listDemoHomeworks(nextState, session.user.id);
      const progress = getDemoProgress(nextState, session.user.id);
      startTransition(() => {
        setStudentSnapshot((current) => ({
          ...current,
          selectedHomework: detail,
          homeworks,
          progress,
          lastHomeworkSubmission: result,
          dashboard: buildStudentDashboardState({
            progress,
            homeworkSummary: homeworks,
            recommendation: current.practiceTask,
          }),
        }));
      });
      pushToast("Homework item saved in demo mode.", result.review_status === "reviewed" ? "success" : "warning");
      return result;
    } finally {
      setLoading((current) => ({ ...current, homework: false }));
    }
  }

  async function loadTeacherDashboard() {
    if (!session || session.user.role !== "teacher") {
      return null;
    }

    setLoading((current) => ({ ...current, teacher: true }));
    try {
      let students;
      let tasks;
      let homeworks;
      let usedDemo = session.mode !== "live";

      if (session.mode === "live") {
        const [studentsResult, tasksResult, homeworksResult] = await Promise.allSettled([
          fetchTeacherStudents(session.token),
          fetchTeacherTasks(session.token),
          fetchTeacherHomeworks(session.token),
        ]);
        if (studentsResult.status === "fulfilled") {
          students = studentsResult.value;
        } else {
          students = getDemoStudentSummaries(demoState);
          usedDemo = true;
        }
        if (tasksResult.status === "fulfilled") {
          tasks = tasksResult.value;
        } else {
          tasks = demoState.tasks;
          usedDemo = true;
        }
        if (homeworksResult.status === "fulfilled") {
          homeworks = homeworksResult.value;
        } else {
          homeworks = getDemoTeacherHomeworks(demoState, session.user.id);
          usedDemo = true;
        }
      } else {
        students = getDemoStudentSummaries(demoState);
        tasks = demoState.tasks;
        homeworks = getDemoTeacherHomeworks(demoState, session.user.id);
      }

      const overview = buildTeacherOverview(students, tasks, homeworks);
      startTransition(() => {
        setTeacherSnapshot((current) => ({
          ...current,
          ...overview,
        }));
      });
      setBackendMode(usedDemo ? "demo" : "live");
      return overview;
    } finally {
      setLoading((current) => ({ ...current, teacher: false }));
    }
  }

  async function loadTeacherHomeworks() {
    const overview = await loadTeacherDashboard();
    return overview?.homeworks || [];
  }

  async function createTask(payload) {
    if (!session || session.user.role !== "teacher") {
      return null;
    }

    if (session.mode === "live") {
      try {
        const task = await createTeacherTask(session.token, payload);
        const tasks = await fetchTeacherTasks(session.token);
        setTeacherSnapshot((current) => ({
          ...current,
          tasks,
          stats: buildTeacherOverview(current.students, tasks, current.homeworks).stats,
        }));
        pushToast("Task created via live API.", "success");
        setBackendMode("live");
        return task;
      } catch {
        setBackendMode("demo");
      }
    }

    const { nextState, result: task } = updateDemo((state) => createDemoTask(state, payload));
    const students = getDemoStudentSummaries(nextState);
    const tasks = nextState.tasks;
    const homeworks = getDemoTeacherHomeworks(nextState, session.user.id);
    setTeacherSnapshot((current) => ({
      ...current,
      students,
      tasks,
      homeworks,
      stats: buildTeacherOverview(students, tasks, homeworks).stats,
    }));
    pushToast("Task created in demo mode.", "success");
    return task;
  }

  async function createHomework(payload) {
    if (!session || session.user.role !== "teacher") {
      return null;
    }

    if (session.mode === "live") {
      try {
        const homework = await createTeacherHomework(session.token, payload);
        const [students, tasks, homeworks] = await Promise.all([
          fetchTeacherStudents(session.token),
          fetchTeacherTasks(session.token),
          fetchTeacherHomeworks(session.token),
        ]);
        setTeacherSnapshot((current) => ({
          ...current,
          students,
          tasks,
          homeworks,
          stats: buildTeacherOverview(students, tasks, homeworks).stats,
        }));
        pushToast("Homework created via live API.", "success");
        setBackendMode("live");
        return homework;
      } catch {
        setBackendMode("demo");
      }
    }

    const { nextState, result: homework } = updateDemo((state) =>
      createDemoHomework(state, session.user.id, payload),
    );
    const students = getDemoStudentSummaries(nextState);
    const tasks = nextState.tasks;
    const homeworks = getDemoTeacherHomeworks(nextState, session.user.id);
    setTeacherSnapshot((current) => ({
      ...current,
      students,
      tasks,
      homeworks,
      stats: buildTeacherOverview(students, tasks, homeworks).stats,
    }));
    pushToast("Homework created in demo mode.", "success");
    return homework;
  }

  async function loadStudentAnalytics(studentId) {
    if (!session || session.user.role !== "teacher") {
      return null;
    }

    if (session.mode === "live") {
      try {
        const progress = await fetchTeacherStudentProgress(session.token, studentId);
        setTeacherSnapshot((current) => ({
          ...current,
          selectedStudentId: studentId,
          selectedStudentProgress: progress,
        }));
        setBackendMode("live");
        return progress;
      } catch {
        setBackendMode("demo");
      }
    }

    const progress = getDemoProgress(demoState, studentId);
    setTeacherSnapshot((current) => ({
      ...current,
      selectedStudentId: studentId,
      selectedStudentProgress: progress,
    }));
    return progress;
  }

  const value = {
    backendMode,
    clearToast,
    createHomework,
    createTask,
    evaluateHomeworkItem,
    evaluatePracticeSubmission,
    loadPracticeTask,
    loadStudentAnalytics,
    loadStudentDashboard,
    loadStudentHomeworks,
    loadStudentProgress,
    loadTeacherDashboard,
    loadTeacherHomeworks,
    loading,
    login,
    logout,
    openHomeworkDetail,
    register,
    session,
    studentSnapshot,
    teacherSnapshot,
    toast,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const value = useContext(AppContext);
  if (!value) {
    throw new Error("useAppContext must be used inside AppProvider");
  }
  return value;
}
