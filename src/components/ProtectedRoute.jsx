import { Navigate, Outlet } from "react-router-dom";
import { ACCESS_TOKEN } from "../constants";

const ProtectedRoute = () => {
  const isAuthenticated = localStorage.getItem(ACCESS_TOKEN);
  // If not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // If authenticated, render the child routes
  return <Outlet />;
};

export default ProtectedRoute; 