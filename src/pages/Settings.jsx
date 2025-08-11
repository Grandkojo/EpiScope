// "use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { SettingsIcon, User, Bell, Shield, Database, Download, Upload, Palette, Globe, Save } from "lucide-react"

const Settings = () => {
  const [activeTab, setActiveTab] = useState("profile")
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    sms: true,
    alerts: true,
  })

  const settingsTabs = [
    { id: "profile", label: "Profile", icon: User },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "security", label: "Security", icon: Shield },
    { id: "data", label: "Data Management", icon: Database },
    { id: "appearance", label: "Appearance", icon: Palette },
    { id: "system", label: "System", icon: Globe },
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case "profile":
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">Full Name</label>
                  <input
                    type="text"
                    defaultValue="Dr. Kwame Asante"
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">Email</label>
                  <input
                    type="email"
                    defaultValue="kwame.asante@health.gov.gh"
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">Department</label>
                  <select className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500">
                    <option>Disease Surveillance</option>
                    <option>Public Health</option>
                    <option>Epidemiology</option>
                    <option>Health Analytics</option>
                  </select>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">Phone</label>
                  <input
                    type="tel"
                    defaultValue="+233 24 123 4567"
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">Region</label>
                  <select className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500">
                    <option>Greater Accra</option>
                    <option>Ashanti</option>
                    <option>Western</option>
                    <option>Eastern</option>
                    <option>Northern</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">Role</label>
                  <select className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500">
                    <option>Administrator</option>
                    <option>Analyst</option>
                    <option>Viewer</option>
                    <option>Regional Coordinator</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )

      case "notifications":
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              {Object.entries(notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-4 rounded-lg border border-border">
                  <div>
                    <h3 className="font-medium text-foreground capitalize">{key} Notifications</h3>
                    <p className="text-sm text-muted-foreground">
                      Receive {key} notifications for health alerts and updates
                    </p>
                  </div>
                  <button
                    onClick={() => setNotifications((prev) => ({ ...prev, [key]: !value }))}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      value ? "bg-health-500" : "bg-gray-600"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        value ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )

      case "data":
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Upload className="h-5 w-5" />
                    <span>Data Import</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Upload CSV File</label>
                    <input
                      type="file"
                      accept=".csv"
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500"
                    />
                  </div>
                  <Button className="w-full">
                    <Upload className="h-4 w-4 mr-2" />
                    Import Data
                  </Button>
                </CardContent>
              </Card>

              <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Download className="h-5 w-5" />
                    <span>Data Export</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Export Format</label>
                    <select className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500">
                      <option>CSV</option>
                      <option>Excel</option>
                      <option>PDF Report</option>
                      <option>JSON</option>
                    </select>
                  </div>
                  <Button variant="outline" className="w-full">
                    <Download className="h-4 w-4 mr-2" />
                    Export Data
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        )

      default:
        return (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Settings for {activeTab} coming soon...</p>
          </div>
        )
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center space-x-3">
            <SettingsIcon className="h-8 w-8 text-health-400" />
            <span>Settings</span>
          </h1>
          <p className="text-muted-foreground">Manage your account and application preferences</p>
        </div>
        <Button>
          <Save className="h-4 w-4 mr-2" />
          Save Changes
        </Button>
      </div>

      {/* Settings Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Navigation */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300 lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Settings</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <nav className="space-y-1">
              {settingsTabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 text-left text-sm transition-colors ${
                      activeTab === tab.id
                        ? "bg-health-600/20 text-health-400 border-r-2 border-health-500"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </nav>
          </CardContent>
        </Card>

        {/* Settings Content */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300 lg:col-span-3">
          <CardHeader>
            <CardTitle className="capitalize">{activeTab} Settings</CardTitle>
          </CardHeader>
          <CardContent>{renderTabContent()}</CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Settings
