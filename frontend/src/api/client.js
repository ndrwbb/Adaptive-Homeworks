import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 1800,
});

function authConfig(token) {
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {};
}

export async function healthCheck() {
  const { data } = await api.get("/health");
  return data;
}

export async function registerUser(payload) {
  const { data } = await api.post("/auth/register", payload);
  return data;
}

export async function loginUser(email, password) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  const { data } = await api.post("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function fetchMe(token) {
  const { data } = await api.get("/auth/me", authConfig(token));
  return data;
}

export async function fetchRecommendation(token, filters = {}) {
  const { data } = await api.get("/tasks/recommendation", {
    ...authConfig(token),
    params: filters,
  });
  return data;
}

export async function submitAnswer(token, payload) {
  const { data } = await api.post("/submissions", payload, authConfig(token));
  return data;
}

export async function fetchMyProgress(token) {
  const { data } = await api.get("/progress/me", authConfig(token));
  return data;
}

export async function fetchMyHistory(token) {
  const { data } = await api.get("/progress/me/history", authConfig(token));
  return data;
}

export async function fetchTeacherTasks(token) {
  const { data } = await api.get("/teacher/tasks", authConfig(token));
  return data;
}

export async function fetchMyHomeworks(token) {
  const { data } = await api.get("/homeworks/my", authConfig(token));
  return data;
}

export async function fetchHomeworkDetail(token, assignmentId) {
  const { data } = await api.get(`/homeworks/my/${assignmentId}`, authConfig(token));
  return data;
}

export async function submitHomeworkItem(token, assignmentId, payload) {
  const { data } = await api.post(
    `/homeworks/my/${assignmentId}/submit-item`,
    payload,
    authConfig(token),
  );
  return data;
}

export async function createTeacherTask(token, payload) {
  const { data } = await api.post("/teacher/tasks", payload, authConfig(token));
  return data;
}

export async function fetchTeacherHomeworks(token) {
  const { data } = await api.get("/teacher/homeworks", authConfig(token));
  return data;
}

export async function createTeacherHomework(token, payload) {
  const { data } = await api.post("/teacher/homeworks", payload, authConfig(token));
  return data;
}

export async function fetchTeacherStudents(token) {
  const { data } = await api.get("/teacher/students", authConfig(token));
  return data;
}

export async function fetchTeacherStudentProgress(token, studentId) {
  const { data } = await api.get(`/teacher/students/${studentId}/progress`, authConfig(token));
  return data;
}

export async function generateTeacherHomework(token, payload) {
  const { data } = await api.post("/teacher/homeworks/generate", payload, authConfig(token));
  return data;
}

export async function fetchTeacherTopics(token) {
  const { data } = await api.get("/teacher/topics", authConfig(token));
  return data;
}
