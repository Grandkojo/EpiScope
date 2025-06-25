import { NavLink } from "react-router-dom"
import {
  Home,
  User,
  HeartPulse,
  BrainCircuit,
  Bell,
  LifeBuoy,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"
import { Button } from "../components/ui/button"

const navItems = [
  { path: "/users", icon: Home, label: "Home", end: true },
  { path: "/users/analytics", icon: User, label: "Analytics" },
  { path: "/users/health trends", icon: HeartPulse, label: "Health Trends" },
  { path: "/users/ai", icon: BrainCircuit, label: "AI" },
  { path: "/users/settings", icon: LifeBuoy, label: "Settings" },

]

const UserSidebar = ({ collapsed, setCollapsed }) => {
  return (
    <aside
      className={`h-screen bg-gray-800 border-r border-gray-200 flex flex-col transition-all duration-300 ${
        collapsed ? "w-16" : "w-56"
      }`}
    >
      {/* Logo and Collapse Arrow */}
      <div className="h-16 flex items-center justify-between px-4">
        <h1 className={`text-xl font-bold text-white transition-all duration-200 ${collapsed ? "hidden" : "block"}`}>EpiScope</h1>
        <div className="flex items-center justify-center h-8 w-8">
          <Button
            variant="default"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4 text-white" />
            ) : (
              <ChevronLeft className="h-4 w-4 text-white" />
            )}
          </Button>
        </div>
      </div>
      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            className={({ isActive }) =>
              `flex items-center ${collapsed ? "justify-center px-0" : "space-x-3 px-3"} py-2 rounded-lg transition-all duration-200 group ${
                isActive
                  ? "bg-blue-600 text-white border border-blue-700"
                  : "hover:bg-gray-700 text-gray-500 hover:text-white"
              }`
            }
          >
            {({ isActive }) => {
              const Icon = item.icon
              return (
                <>
                  <Icon className={`h-5 w-5 transition-colors ${
                    isActive
                      ? "text-white"
                      : "text-gray-400 group-hover:text-white"
                  }`} />
                  {!collapsed && (
                    <span className="text-sm font-medium truncate ml-3">{item.label}</span>
                  )}
                </>
              )
            }}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default UserSidebar 