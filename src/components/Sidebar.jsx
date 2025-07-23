"use client"

import { useState } from "react"
import { Link, useLocation } from "react-router-dom"
import {
  LayoutDashboard,
  BarChart3,
  MapPin,
  Activity,
  Settings,
  ChevronLeft,
  ChevronRight,
  Heart,
  Droplets,
} from "lucide-react"
import Logo from "./Logo"
import { Button } from "./ui/button"
import { cn } from "@/lib/utils"

const Sidebar = ({ collapsed, setCollapsed }) => {
  const location = useLocation()

  const menuItems = [
    {
      title: "Dashboard",
      icon: LayoutDashboard,
      path: "/",
      description: "Overview & Analytics",
    },
    {
      title: "Analytics",
      icon: BarChart3,
      path: "/analytics",
      description: "Data Insights",
    },
    {
      title: "Hotspots",
      icon: MapPin,
      path: "/hotspots",
      description: "Geographic Data",
    },
    {
      title: "Diabetes",
      icon: Heart,
      path: "/diabetes",
      description: "Diabetes Monitoring",
    },
    {
      title: "Malaria",
      icon: Droplets,
      path: "/malaria",
      description: "Malaria Tracking",
    },
    {
      title: "Health Trends",
      icon: Activity,
      path: "/trends",
      description: "Trend Analysis",
    },
    {
      title: "Settings",
      icon: Settings,
      path: "/settings",
      description: "Configuration",
    },
  ]

  return (
    <aside className={cn(
      "h-screen bg-gray-800 text-gray-200 flex flex-col z-40 border-r border-gray-900 transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Header */}
      <div className="p-4 border-b border-gray-900 flex items-center justify-between">
        <div className={cn("flex items-center space-x-3 transition-opacity duration-200", collapsed && "opacity-0 w-0 overflow-hidden")}> 
          <Logo className="w-8 h-8" />
          <div>
            <h1 className="text-xl font-bold text-white">Episcope</h1>
            <p className="text-xs text-gray-400">Health Monitor</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={() => setCollapsed(!collapsed)} className="h-8 w-8">
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>
      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + "/")
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 group",
                isActive
                  ? "bg-blue-600 text-white border border-blue-700"
                  : "hover:bg-gray-700 hover:text-white",
                collapsed && "justify-center px-0"
              )}
            >
              <Icon className={cn("h-5 w-5 transition-colors", isActive ? "text-blue-400" : "text-gray-400")} />
              {!collapsed && (
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{item.title}</p>
                  <p className={isActive ? "text-xs text-white truncate" : "text-xs text-gray-500 truncate"}>{item.description}</p>
                </div>
              )}
            </Link>
          )
        })}
      </nav>
      {/* Footer */}
      <div className="p-4 border-t border-gray-900 mt-auto">
        <div className={cn("text-center transition-opacity duration-200", collapsed && "opacity-0 w-0 overflow-hidden")}> 
          <p className="text-xs text-gray-400">Ghana Health Monitor</p>
          <p className="text-xs text-blue-400 font-medium">v1.0.0</p>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
