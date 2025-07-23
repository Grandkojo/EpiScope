// "use client"

import { useNotification } from "../contexts/notification-context"

export function useNotificationHelpers() {
  const { addNotification } = useNotification()

  const showSuccess = (message, title = "Success!", duration = 3000) => {
    return addNotification({
      type: "success",
      title,
      message,
      duration,
    })
  }

  const showError = (message, title = "Error!", duration = 3000) => {
    return addNotification({
      type: "error",
      title,
      message,
      duration,
    })
  }

  const showWarning = (message, title = "Warning!", duration = 3000) => {
    return addNotification({
      type: "warning",
      title,
      message,
      duration,
    })
  }

  const showInfo = (message, title = "Info", duration = 3000) => {
    return addNotification({
      type: "info",
      title,
      message,
      duration,
    })
  }

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
  }
}
