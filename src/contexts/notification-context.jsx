"use client"

import { createContext, useContext, useState, useCallback } from "react"

const NotificationContext = createContext()

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([])

  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random()
    const newNotification = {
      id,
      type: "info",
      duration: 3000,
      ...notification,
    }

    // console.log("Adding notification:", newNotification)
    setNotifications((prev) => [...prev, newNotification])

    // Auto-remove after specified duration
    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }

    return id
  }, [])

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id))
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  const queueNotification = useCallback((notification) => {
    const newNotification = {
      type: "info",
      duration: 3000,
      ...notification,
    }

    try {
      const existing = JSON.parse(sessionStorage.getItem("queuedNotifications") || "[]")
      existing.push(newNotification)
      sessionStorage.setItem("queuedNotifications", JSON.stringify(existing))
      // console.log("Successfully queued notification:", newNotification)
    } catch (error) {
      console.error("Failed to queue notification:", error)
    }
  }, [])

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        addNotification,
        removeNotification,
        clearAll,
        queueNotification,
      }}
    >
      {children}
    </NotificationContext.Provider>
  )
}

export function useNotification() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error("useNotification must be used within a NotificationProvider")
  }
  return context
}
