import { Navigate } from "react-router-dom";

import { useAppContext } from "../context/AppContext";

import ProtectedRoute from "./ProtectedRoute";

export default function RoleRoute({ children, role }) {
  const { session } = useAppContext();

  return (
    <ProtectedRoute>
      {session?.user?.role === role ? children : <Navigate to="/" replace />}
    </ProtectedRoute>
  );
}
