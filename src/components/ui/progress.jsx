import React from "react"
import clsx from "clsx"

export function Progress({ value = 0, className }) {
  return (
    <div className={clsx("w-full h-2 bg-gray-200 rounded", className)}>
      <div
        className="h-full bg-green-500 rounded transition-all duration-500"
        style={{ width: `${value}%` }}
      />
    </div>
  )
}
