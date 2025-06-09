import { Search, User } from "lucide-react"

const UserHeader = () => {
  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center relative">
      {/* Left: Title */}
      <div className="flex items-center min-w-0">
        <h2 className="text-lg font-semibold text-gray-900 whitespace-nowrap">User Dashboard</h2>
      </div>
      {/* Center: Search */}
      <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[320px]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search your health data..."
            className="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full transition-all text-gray-900"
          />
        </div>
      </div>
      {/* Right: User Icon */}
      <div className="flex items-center space-x-4 ml-auto">
        <button className="bg-gray-100 rounded-full p-2 border border-gray-200">
          <User className="h-5 w-5 text-gray-900" />
        </button>
      </div>
    </header>
  )
}

export default UserHeader 