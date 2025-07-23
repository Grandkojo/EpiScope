import React, { useState } from "react"

export function Tabs({ defaultValue, children, className = "" }) {
  const [activeTab, setActiveTab] = useState(defaultValue)

  const triggerList = []
  const contentList = []

  React.Children.forEach(children, (child) => {
    if (child.type === TabsList) {
      triggerList.push(React.cloneElement(child, { activeTab, setActiveTab }))
    } else if (child.type === TabsContent && child.props.value === activeTab) {
      contentList.push(child)
    }
  })

  return (
    <div className={className}>
      {triggerList}
      {contentList}
    </div>
  )
}

export function TabsList({ children, activeTab, setActiveTab }) {
  return (
    <div className="flex gap-2 mb-4">
      {React.Children.map(children, (child) =>
        React.cloneElement(child, { activeTab, setActiveTab })
      )}
    </div>
  )
}

export function TabsTrigger({ value, children, activeTab, setActiveTab }) {
  const isActive = activeTab === value
  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`px-4 py-2 rounded ${
        isActive ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-800"
      }`}
    >
      {children}
    </button>
  )
}

export function TabsContent({ value, children }) {
  return <div>{children}</div>
}
