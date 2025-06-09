import { useState } from "react"
import { Outlet } from "react-router-dom"
import UserSidebar from "./UserSidebar"
import UserHeader from "./UserHeader"

const UserLayout = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 flex">
      <UserSidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
      <div className="flex-1 flex flex-col h-screen overflow-hidden transition-all duration-300">
        <UserHeader />
        <main className="flex-1 w-full overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default UserLayout 