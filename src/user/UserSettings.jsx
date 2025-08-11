import { useState } from "react";
import { Save, BrainCircuit, Settings as SettingsIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";

const UserSettings = () => {
  const [activeTab, setActiveTab] = useState("ai");
  const [aiEnabled, setAiEnabled] = useState(false);

  const settingsTabs = [
    { id: "ai", label: "AI Assistance", icon: BrainCircuit },
  ];

  const renderTabContent = () => {
    if (activeTab === "ai") {
      return (
        <div className="space-y-6">
          <div className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300 flex items-center justify-between p-4">
            <div>
              <h3 className="font-medium text-foreground">Enable AI Assistance</h3>
              <p className="text-sm text-muted-foreground">
                Let AI assist you with recommendations and insights.
              </p>
            </div>
            <button
              onClick={() => setAiEnabled(!aiEnabled)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                aiEnabled ? "bg-green-500" : "bg-gray-500"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  aiEnabled ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
          <p className="text-sm text-muted-foreground">
            AI Assistance is <strong>{aiEnabled ? "enabled" : "disabled"}</strong>.
          </p>
        </div>
      );
    }

    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Settings for {activeTab} coming soon...</p>
      </div>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center space-x-3">
            <SettingsIcon className="h-8 w-8 text-health-400" />
            <span>User Settings</span>
          </h1>
          <p className="text-muted-foreground">Manage your personal preferences</p>
        </div>
        <Button>
          <Save className="h-4 w-4 mr-2" />
          Save Changes
        </Button>
      </div>

      {/* Settings Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Tabs */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300 lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Settings</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <nav className="space-y-1">
              {settingsTabs.map((tab) => {
                const Icon = tab.icon;
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
                );
              })}
            </nav>
          </CardContent>
        </Card>

        {/* Content */}
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

export default UserSettings;
