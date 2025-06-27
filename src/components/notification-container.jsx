"use client"

import { useNotification } from "../contexts/notification-context"
import { Notification } from "./notification"

export function NotificationContainer() {
  const { notifications, removeNotification } = useNotification()

  if (notifications.length === 0) return null

  return (
    <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4">
      <div className="space-y-2">
        {notifications.map((notification) => (
          <Notification key={notification.id} notification={notification} onClose={removeNotification} />
        ))}
      </div>
    </div>
  )
}
