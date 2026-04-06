import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import RoleRoute from "./components/RoleRoute";
import { AppProvider } from "./context/AppContext";
import Home from "./pages/Home";
import HomeworkDetailPage from "./pages/HomeworkDetailPage";
import HomeworksPage from "./pages/HomeworksPage";
import Login from "./pages/Login";
import ProgressPage from "./pages/ProgressPage";
import Register from "./pages/Register";
import SelfEducationPage from "./pages/SelfEducationPage";
import StudentAnalytics from "./pages/StudentAnalytics";
import StudentDashboard from "./pages/StudentDashboard";
import TaskManager from "./pages/TaskManager";
import TeacherDashboard from "./pages/TeacherDashboard";
import TeacherHomeworksPage from "./pages/TeacherHomeworksPage";

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/student"
              element={
                <RoleRoute role="student">
                  <StudentDashboard />
                </RoleRoute>
              }
            />
            <Route
              path="/student/homeworks"
              element={
                <RoleRoute role="student">
                  <HomeworksPage />
                </RoleRoute>
              }
            />
            <Route
              path="/student/homeworks/:assignmentId"
              element={
                <RoleRoute role="student">
                  <HomeworkDetailPage />
                </RoleRoute>
              }
            />
            <Route
              path="/student/self-education"
              element={
                <RoleRoute role="student">
                  <SelfEducationPage />
                </RoleRoute>
              }
            />
            <Route
              path="/student/progress"
              element={
                <RoleRoute role="student">
                  <ProgressPage />
                </RoleRoute>
              }
            />
            <Route
              path="/teacher"
              element={
                <RoleRoute role="teacher">
                  <TeacherDashboard />
                </RoleRoute>
              }
            />
            <Route
              path="/teacher/tasks"
              element={
                <RoleRoute role="teacher">
                  <TaskManager />
                </RoleRoute>
              }
            />
            <Route
              path="/teacher/homeworks"
              element={
                <RoleRoute role="teacher">
                  <TeacherHomeworksPage />
                </RoleRoute>
              }
            />
            <Route
              path="/teacher/students"
              element={
                <RoleRoute role="teacher">
                  <StudentAnalytics />
                </RoleRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </AppProvider>
    </BrowserRouter>
  );
}
