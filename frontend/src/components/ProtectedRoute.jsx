import { Navigate, useLocation } from "react-router-dom";

import { useAppContext } from "../context/AppContext";

export default function ProtectedRoute({ children }) {
  const { session } = useAppContext();
  const location = useLocation();

  if (!session) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return children;
}
