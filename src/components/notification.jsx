"use client"

import { useState, useEffect } from "react"
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react"

const notificationStyles = {
  success: {
    bg: "bg-green-50 border-green-200",
    text: "text-green-800",
    icon: CheckCircle,
    iconColor: "text-green-400",
  },
  error: {
    bg: "bg-red-50 border-red-200",
    text: "text-red-800",
    icon: AlertCircle,
    iconColor: "text-red-400",
  },
  warning: {
    bg: "bg-yellow-50 border-yellow-200",
    text: "text-yellow-800",
    icon: AlertTriangle,
    iconColor: "text-yellow-400",
  },
  info: {
    bg: "bg-blue-50 border-blue-200",
    text: "text-blue-800",
    icon: Info,
    iconColor: "text-blue-400",
  },
}

export function Notification({ notification, onClose }) {
  const [isVisible, setIsVisible] = useState(false)
  const [isLeaving, setIsLeaving] = useState(false)

  const style = notificationStyles[notification.type] || notificationStyles.info
  const IconComponent = style.icon

  useEffect(() => {
    // Trigger entrance animation
    const timer = setTimeout(() => setIsVisible(true), 10)
    return () => clearTimeout(timer)
  }, [])

  const handleClose = () => {
    setIsLeaving(true)
    setTimeout(() => {
      onClose(notification.id)
    }, 300) // Match the exit animation duration
  }

  return (
    <div
      className={`
        relative flex items-center gap-3 p-4 mb-3 border rounded-lg shadow-lg backdrop-blur-sm
        transition-all duration-300 ease-in-out transform
        ${style.bg} ${style.text}
        ${
          isVisible && !isLeaving
            ? "translate-y-0 opacity-100 scale-100"
            : isLeaving
              ? "-translate-y-2 opacity-0 scale-95"
              : "translate-y-2 opacity-0 scale-95"
        }
      `}
      role="alert"
      aria-live="polite"
    >
      {/* Icon */}
      <IconComponent className={`h-5 w-5 flex-shrink-0 ${style.iconColor}`} />

      {/* Content */}
      <div className="flex-1 min-w-0">
        {notification.title && <h4 className="font-medium text-sm mb-1">{notification.title}</h4>}
        <p className="text-sm">{notification.message}</p>
      </div>

      {/* Close Button */}
      <button
        onClick={handleClose}
        className={`
          flex-shrink-0 p-1 rounded-full transition-colors duration-200
          hover:bg-black/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current
        `}
        aria-label="Close notification"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}
