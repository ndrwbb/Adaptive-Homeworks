import { Navigate } from "react-router-dom";

import { useAppContext } from "../context/AppContext";
import StudentDashboard from "../pages/StudentDashboard";
import TeacherDashboard from "../pages/TeacherDashboard";

export default function DashboardRouter() {
  const { session } = useAppContext();

  if (!session) {
    return <Navigate to="/login" replace />;
  }

  return session.user.role === "teacher" ? <TeacherDashboard /> : <StudentDashboard />;
}
