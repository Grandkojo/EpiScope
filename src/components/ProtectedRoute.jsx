import { Navigate, Outlet } from "react-router-dom";
import { ACCESS_TOKEN, ACCESS_TOKEN_LIFETIME } from "../constants";

const ProtectedRoute = () => {
  const isAuthenticated = localStorage.getItem(ACCESS_TOKEN);
  const tokenExpiry = localStorage.getItem(ACCESS_TOKEN_LIFETIME);
  const isTokenExpired = Date.now() > parseInt(tokenExpiry, 10);

  // If not authenticated, redirect to login
  if (!isAuthenticated || isTokenExpired) {
    return <Navigate to="/login" replace />;
  }

  // If authenticated, render the child routes
  return <Outlet />;
};

export default ProtectedRoute; 