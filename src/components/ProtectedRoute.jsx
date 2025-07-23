import { Navigate, Outlet } from "react-router-dom";
import api from "../api";
import { ACCESS_TOKEN, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN } from "../constants";
import { useState, useEffect } from "react";

const ProtectedRoute = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const tokenExpiry = localStorage.getItem(ACCESS_TOKEN_LIFETIME);
    const accessToken = localStorage.getItem(ACCESS_TOKEN);
    const refreshToken = localStorage.getItem(REFRESH_TOKEN);
    
    // If no tokens exist, redirect to login
    if (!accessToken || !tokenExpiry || !refreshToken) {
      clearAuthData();
      setIsAuthenticated(false);
      setIsLoading(false);
      return;
    }

    const isTokenExpired = Date.now() > tokenExpiry;

    if (isTokenExpired) {
      // Try to refresh the token
      try {
        const response = await api.post('/auth/user/refresh/', {
          refresh: refreshToken
        });
        
        const access  = response.data.access;
        localStorage.setItem(ACCESS_TOKEN, access);
        const expiryTimestamp = Date.now() + ACCESS_TOKEN_LIFETIME
        localStorage.setItem(ACCESS_TOKEN_LIFETIME, expiryTimestamp)
        
        setIsAuthenticated(true);
      } catch (error) {
        // Refresh failed, clear auth data and redirect to login
        clearAuthData();
        setIsAuthenticated(false);
      }
    } else {
      setIsAuthenticated(true);
    }
    
    setIsLoading(false);
  };

  if (isLoading) {
    return <div>Loading...</div>; // You can replace this with a proper loading component
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Token is valid, render the protected content
  return <Outlet />;
};

// Helper function to clear authentication data
const clearAuthData = () => {
  localStorage.removeItem(ACCESS_TOKEN);
  localStorage.removeItem(ACCESS_TOKEN_LIFETIME);
  localStorage.removeItem(REFRESH_TOKEN);
};

export default ProtectedRoute; 