// "use client"

import { useCallback } from "react"
import { useNotification } from "../contexts/notification-context"
import { useNavigate, useSearchParams } from "react-router-dom"
import { useEffect } from "react"

export function useCrossPageNotifications() {
  const { queueNotification } = useNotification()
  const navigate  = useNavigate()

  const showOnNextPage = useCallback(
    (notification, redirectTo) => {
      // console.log("Queueing notification for next page:", notification)
      queueNotification(notification)

      if (redirectTo) {
        // Small delay to ensure sessionStorage is written
        setTimeout(() => {
          // console.log("Navigating to:", redirectTo)
          navigate(redirectTo)
        }, 100)
      }
    },
    [queueNotification, navigate],
  )

  const showViaUrl = useCallback(
    (notification, redirectTo) => {
      const params = new URLSearchParams()
      params.set("notificationType", notification.type)
      params.set("notificationTitle", notification.title || "")
      params.set("notificationMessage", notification.message || "")

      const url = `${redirectTo}?${params.toString()}`
      navigate(url)
    },
    [navigate],
  )

  return {
    showOnNextPage,
    showViaUrl,
  }
}

export function useUrlNotifications() {
  const { addNotification } = useNotification()
  const searchParams = useSearchParams()

  useEffect(() => {
    if (!searchParams) return

    const type = searchParams.get("notificationType")
    const title = searchParams.get("notificationTitle")
    const message = searchParams.get("notificationMessage")

    if (type && message) {
      // console.log("Found URL notification:", { type, title, message })

      addNotification({
        type,
        title: title || undefined,
        message,
      })

      // Clean up URL parameters
      if (typeof window !== "undefined") {
        const url = new URL(window.location)
        url.searchParams.delete("notificationType")
        url.searchParams.delete("notificationTitle")
        url.searchParams.delete("notificationMessage")
        window.history.replaceState({}, "", url.pathname + url.search)
      }
    }
  }, [searchParams, addNotification])
}
