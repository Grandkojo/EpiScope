<header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between">
  <div className="flex items-center space-x-4">
    <div>
      <h2 className="text-lg font-semibold text-gray-900">Health Dashboard</h2>
      <div className="flex items-center space-x-2 text-sm text-gray-500">
        <Calendar className="h-4 w-4" />
        <span>{currentDate}</span>
      </div>
    </div>
  </div>
  <div className="flex items-center space-x-4">
    {/* Search */}
    <div className="relative">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500" />
      <input
        type="text"
        placeholder="Search health data..."
        className="pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-600 focus:border-transparent w-64"
      />
    </div>
    {/* Notifications */}
    <Button variant="ghost" size="icon" className="relative">
      <Bell className="h-5 w-5" />
      <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs flex items-center justify-center text-white">
        3
      </span>
    </Button>
    {/* User Profile */}
    <Button variant="ghost" size="icon">
      <User className="h-5 w-5" />
    </Button>
  </div>
</header> 