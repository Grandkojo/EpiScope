import { Bell, Search, User, Calendar } from "lucide-react"
import { Button } from "./ui/button"

const Header = ({ sidebarCollapsed, setSidebarCollapsed }) => {
  const currentDate = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  })

  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center relative">
      {/* Left: Title and Date */}
      <div className="flex items-center space-x-4 min-w-0">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 whitespace-nowrap">Health Dashboard</h2>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Calendar className="h-4 w-4" />
            <span>{currentDate}</span>
          </div>
        </div>
      </div>
      {/* Center: Search */}
      <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[480px]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search for diseases, regions, or metrics..."
            className="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full transition-all text-gray-900"
          />
        </div>
      </div>
      {/* Right: Notification and User */}
      <div className="flex items-center space-x-4 ml-auto">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5 text-gray-900" />
          <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs flex items-center justify-center text-white">
            3
          </span>
        </Button>
        <Button variant="ghost" size="icon">
          <User className="h-5 w-5 text-gray-900" />
        </Button>
      </div>
    </header>
  )
}

export default Header
