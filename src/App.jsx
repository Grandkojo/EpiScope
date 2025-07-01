import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./components/ThemeProvider";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import Diabetes from "./pages/Diabetes";
import Malaria from "./pages/Malaria";
import Hotspots from "./pages/Hotspots";
import Trends from "./pages/Trends";
import Settings from "./pages/Settings";
import UserLayout from "./user/UserLayout";
import UserDashboard from "./user/UserDashboard";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ProtectedRoute from "./components/ProtectedRoute";
import UserSettings from "./user/UserSettings";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NotificationProvider } from "./contexts/notification-context"
import { NotificationContainer } from "./components/notification-container"

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <NotificationProvider>
        <ThemeProvider>
          <Router>
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<Dashboard />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="diabetes" element={<Diabetes />} />
                <Route path="malaria" element={<Malaria />} />
                <Route path="hotspots" element={<Hotspots />} />
                <Route path="trends" element={<Trends />} />
                <Route path="settings" element={<Settings />} />
              </Route>
              <Route path="landing" element={<Landing />} />
              <Route path="login" element={<Login />}></Route>
              <Route path="signup" element={<Signup />}></Route>

              {/* Protected User Routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/users/*" element={<UserLayout />}>
                  <Route index element={<UserDashboard />} />
                  <Route path="settings" element={<UserSettings/>}></Route>
                </Route>
              </Route>
            </Routes>
          </Router>
        </ThemeProvider>
        <NotificationContainer />
      </NotificationProvider>
    </QueryClientProvider>
  );
}

export default App;
