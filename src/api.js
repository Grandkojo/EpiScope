import axios from 'axios';
import { ACCESS_TOKEN, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN } from './constants';

const apiUrl = import.meta.env.VITE_API_URL;
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL : apiUrl,
})

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token){
            config.headers.Authorization = `Bearer ${token}`
        }
        return config;
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Add response interceptor to handle 401 errors with token refresh
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            const refreshToken = localStorage.getItem(REFRESH_TOKEN);
            
            if (refreshToken) {
                try {
                    // Try to refresh the token
                    const response = await axios.post(`${apiUrl}auth/user/refresh/`, {
                        refresh: refreshToken
                    });
                    
                    const access = response.data.access;
                    localStorage.setItem(ACCESS_TOKEN, access);
                    const expiryTimestamp = Date.now() + (5 * 60 * 1000); // 5 minutes
                    localStorage.setItem(ACCESS_TOKEN_LIFETIME, expiryTimestamp);
                    
                    // Retry the original request with new token
                    originalRequest.headers.Authorization = `Bearer ${access}`;
                    return api(originalRequest);
                } catch (refreshError) {
                    // Refresh failed, clear auth data and redirect to login
                    localStorage.removeItem(ACCESS_TOKEN);
                    localStorage.removeItem(ACCESS_TOKEN_LIFETIME);
                    localStorage.removeItem(REFRESH_TOKEN);
                    
                    // Show error message and redirect
                    window.location.href = '/login/';
                }
            } else {
                // No refresh token, clear auth data and redirect to login
                localStorage.removeItem(ACCESS_TOKEN);
                localStorage.removeItem(ACCESS_TOKEN_LIFETIME);
                localStorage.removeItem(REFRESH_TOKEN);
                
                window.location.href = '/login/';
            }
        }
        
        return Promise.reject(error);
    }
)

export default api