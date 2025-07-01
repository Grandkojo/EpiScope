"use client"

import { useEffect } from "react"
import { useNotification } from "../contexts/notification-context"

export function useQueuedNotifications() {
  const { addNotification } = useNotification()

  useEffect(() => {
    const checkAndShowQueuedNotifications = () => {
      try {
        const stored = sessionStorage.getItem("queuedNotifications")
        // console.log("Checking for queued notifications:", stored)

        if (stored) {
          const notifications = JSON.parse(stored)
          if (notifications.length > 0) {
            // console.log("Found queued notifications, showing them:", notifications)

            // Clear from storage immediately
            sessionStorage.removeItem("queuedNotifications")

            // Show each notification with a small delay
            notifications.forEach((notification, index) => {
              setTimeout(() => {
                // console.log("Displaying notification:", notification)
                addNotification(notification)
              }, index * 200)
            })
          }
        }
      } catch (error) {
        console.error("Error processing queued notifications:", error)
      }
    }

    // Run immediately when component mounts
    checkAndShowQueuedNotifications()
  }, [addNotification])
}
