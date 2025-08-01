"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import  Badge  from "../components/ui/Badge"
import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar"
import { Progress } from "../components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs"
import {
  Brain,
  Activity,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Target,
  BarChart3,
  Settings,
  Download,
  RefreshCw,
  Star,
  Award,
  Shield,
  Database,
  MessageSquare,
  FileText,
  Globe,
  Bot,
} from "lucide-react"
import EpiScopeHealthChatbot from "../components/EpiScopeHealthChatbot"
// Dummy user data
const userData = {
  profile: {
    id: "ai-001",
    name: "EpiScope AI Assistant",
    aiType: "Epidemic Analysis AI",
    role: "Senior Health Data Analyst",
    avatar: "/placeholder.svg?height=120&width=120",
    status: "active",
    version: "v2.4.1",
    lastActive: "2 minutes ago",
    joinDate: "January 2024",
    location: "Global Health Network",
    specialization: ["Disease Pattern Recognition", "Predictive Modeling", "Risk Assessment"],
  },
  stats: {
    totalTasks: 15420,
    completedTasks: 14890,
    successRate: 96.6,
    averageResponseTime: 0.8,
    dataProcessed: 2.4,
    modelsDeployed: 12,
    alertsGenerated: 3240,
    accuracyScore: 98.2,
  },
  performance: {
    efficiency: 94,
    accuracy: 98,
    reliability: 96,
    speed: 92,
  },
  recentActivities: [
    {
      id: 1,
      type: "analysis",
      title: "Malaria outbreak pattern analysis completed",
      description: "Analyzed 15,000 data points across 5 regions",
      timestamp: "2 minutes ago",
      status: "completed",
      priority: "high",
    },
    {
      id: 2,
      type: "prediction",
      title: "Generated risk assessment for Region A",
      description: "Predicted 15% increase in diabetes cases",
      timestamp: "15 minutes ago",
      status: "completed",
      priority: "medium",
    },
    {
      id: 3,
      type: "alert",
      title: "Critical threshold alert triggered",
      description: "Cholera cases exceeded warning level in Zone C",
      timestamp: "1 hour ago",
      status: "active",
      priority: "critical",
    },
    {
      id: 4,
      type: "report",
      title: "Weekly health trends report generated",
      description: "Comprehensive analysis of 7-day health data",
      timestamp: "2 hours ago",
      status: "completed",
      priority: "low",
    },
    {
      id: 5,
      type: "model",
      title: "Updated predictive model v2.4.1",
      description: "Enhanced accuracy by 2.3% with new algorithms",
      timestamp: "4 hours ago",
      status: "completed",
      priority: "medium",
    },
  ],
  interactions: [
    {
      id: 1,
      user: "Dr. Sarah Johnson",
      query: "What's the current malaria trend in Southeast Asia?",
      response: "Malaria cases have decreased by 12% compared to last month...",
      timestamp: "5 minutes ago",
      satisfaction: 5,
    },
    {
      id: 2,
      user: "Health Ministry Team",
      query: "Generate risk assessment for upcoming flu season",
      response: "Based on historical data and current patterns...",
      timestamp: "20 minutes ago",
      satisfaction: 4,
    },
    {
      id: 3,
      user: "Dr. Michael Chen",
      query: "Analyze diabetes correlation with urban density",
      response: "Strong correlation found (r=0.78) between urban density...",
      timestamp: "1 hour ago",
      satisfaction: 5,
    },
  ],
  achievements: [
    { name: "Data Master", description: "Processed over 1M data points", icon: Database, earned: true },
    { name: "Accuracy Expert", description: "Maintained 95%+ accuracy for 6 months", icon: Target, earned: true },
    { name: "Speed Demon", description: "Average response time under 1 second", icon: Zap, earned: true },
    { name: "Alert Guardian", description: "Generated 1000+ critical alerts", icon: Shield, earned: true },
    { name: "Model Innovator", description: "Deployed 10+ ML models", icon: Brain, earned: false },
    { name: "Global Impact", description: "Served users from 50+ countries", icon: Globe, earned: false },
  ],
}

// Animated counter component
function AnimatedCounter({ end, duration = 2000, suffix = "", decimals = 0 }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTime
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      const value = progress * end
      setCount(decimals > 0 ? Number.parseFloat(value.toFixed(decimals)) : Math.floor(value))
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    requestAnimationFrame(animate)
  }, [end, duration, decimals])

  return (
    <span>
      {count.toLocaleString()}
      {suffix}
    </span>
  )
}

// Status indicator component
function StatusIndicator({ status }) {
  const statusConfig = {
    active: { color: "bg-green-500", text: "Active", textColor: "text-green-700" },
    idle: { color: "bg-yellow-500", text: "Idle", textColor: "text-yellow-700" },
    offline: { color: "bg-gray-500", text: "Offline", textColor: "text-gray-700" },
  }

  const config = statusConfig[status] || statusConfig.offline

  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${config.color} animate-pulse`} />
      <span className={`text-sm font-medium ${config.textColor}`}>{config.text}</span>
    </div>
  )
}

// Activity item component
function ActivityItem({ activity }) {
  const getIcon = (type) => {
    const icons = {
      analysis: BarChart3,
      prediction: TrendingUp,
      alert: AlertCircle,
      report: FileText,
      model: Brain,
    }
    return icons[type] || Activity
  }

  const getPriorityColor = (priority) => {
    const colors = {
      critical: "bg-red-100 text-red-800 border-red-200",
      high: "bg-orange-100 text-orange-800 border-orange-200",
      medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
      low: "bg-green-100 text-green-800 border-green-200",
    }
    return colors[priority] || colors.low
  }

  const Icon = getIcon(activity.type)

  return (
    <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <div className="p-2 bg-blue-100 rounded-full">
        <Icon className="h-4 w-4 text-blue-600" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <h4 className="font-medium text-gray-900 text-sm">{activity.title}</h4>
          <Badge variant="outline" className={`${getPriorityColor(activity.priority)} text-xs`}>
            {activity.priority}
          </Badge>
        </div>
        <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
        <div className="flex items-center gap-4 mt-2">
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Clock className="h-3 w-3" />
            {activity.timestamp}
          </div>
          <Badge
            variant="outline"
            className={
              activity.status === "completed"
                ? "bg-green-50 text-green-700 border-green-200"
                : "bg-blue-50 text-blue-700 border-blue-200"
            }
          >
            {activity.status}
          </Badge>
        </div>
      </div>
    </div>
  )
}

// Interaction item component
function InteractionItem({ interaction }) {
  return (
    <div className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="text-xs">
              {interaction.user
                .split(" ")
                .map((n) => n[0])
                .join("")}
            </AvatarFallback>
          </Avatar>
          <div>
            <p className="font-medium text-sm text-gray-900">{interaction.user}</p>
            <p className="text-xs text-gray-500">{interaction.timestamp}</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              className={`h-3 w-3 ${i < interaction.satisfaction ? "text-yellow-400 fill-current" : "text-gray-300"}`}
            />
          ))}
        </div>
      </div>
      <div className="space-y-2">
        <div className="bg-white p-3 rounded border-l-4 border-blue-500">
          <p className="text-sm text-gray-700">
            <span className="font-medium">Query:</span> {interaction.query}
          </p>
        </div>
        <div className="bg-blue-50 p-3 rounded border-l-4 border-green-500">
          <p className="text-sm text-gray-700">
            <span className="font-medium">Response:</span> {interaction.response}
          </p>
        </div>
      </div>
    </div>
  )
}

// Achievement badge component
function AchievementBadge({ achievement }) {
  const Icon = achievement.icon

  return (
    <div
      className={`p-4 rounded-lg border-2 transition-all ${
        achievement.earned
          ? "bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200 shadow-sm"
          : "bg-gray-50 border-gray-200 opacity-60"
      }`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`p-2 rounded-full ${
            achievement.earned ? "bg-yellow-100 text-yellow-600" : "bg-gray-100 text-gray-400"
          }`}
        >
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <h4 className={`font-medium ${achievement.earned ? "text-gray-900" : "text-gray-500"}`}>
            {achievement.name}
          </h4>
          <p className={`text-sm ${achievement.earned ? "text-gray-600" : "text-gray-400"}`}>
            {achievement.description}
          </p>
        </div>
      </div>
      {achievement.earned && (
        <div className="mt-2">
          <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">Earned</Badge>
        </div>
      )}
    </div>
  )
}

export default function UserAIProfile() {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 1500)
  }

  return (

    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Profile Dashboard</h1>
            <p className="text-gray-600">Monitor AI performance, activities, and interactions</p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center gap-2 bg-transparent"
            >
              <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button variant="outline" size="sm" className="flex items-center gap-2 bg-transparent">
              <Download className="h-4 w-4" />
              Export
            </Button>
            <Button size="sm" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Settings
            </Button>
          </div>
        </div>
        <EpiScopeHealthChatbot />
        {/* Profile Header */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row lg:items-center gap-6">
              <div className="flex items-center gap-6">
                <Avatar className="h-24 w-24 border-4 border-blue-100">
                  <AvatarImage src={userData.profile.avatar || "/placeholder.svg"} alt={userData.profile.name} />
                  <AvatarFallback className="text-2xl font-bold bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                    AI
                  </AvatarFallback>
                </Avatar>
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h2 className="text-2xl font-bold text-gray-900">{userData.profile.name}</h2>
                    <StatusIndicator status={userData.profile.status} />
                  </div>
                  <p className="text-lg text-gray-600 mb-1">{userData.profile.aiType}</p>
                  <p className="text-sm text-gray-500 mb-3">{userData.profile.role}</p>
                  <div className="flex flex-wrap gap-2">
                    {userData.profile.specialization.map((spec, index) => (
                      <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800">
                        {spec}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              <div className="lg:ml-auto grid grid-cols-2 lg:grid-cols-1 gap-4 lg:text-right">
                <div>
                  <p className="text-sm text-gray-500">Version</p>
                  <p className="font-semibold text-gray-900">{userData.profile.version}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Last Active</p>
                  <p className="font-semibold text-gray-900">{userData.profile.lastActive}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Join Date</p>
                  <p className="font-semibold text-gray-900">{userData.profile.joinDate}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Location</p>
                  <p className="font-semibold text-gray-900">{userData.profile.location}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              title: "Total Tasks",
              value: userData.stats.totalTasks,
              icon: CheckCircle,
              color: "text-blue-600",
              bgColor: "bg-blue-50",
              suffix: "",
            },
            {
              title: "Success Rate",
              value: userData.stats.successRate,
              icon: Target,
              color: "text-green-600",
              bgColor: "bg-green-50",
              suffix: "%",
              decimals: 1,
            },
            {
              title: "Avg Response",
              value: userData.stats.averageResponseTime,
              icon: Zap,
              color: "text-yellow-600",
              bgColor: "bg-yellow-50",
              suffix: "s",
              decimals: 1,
            },
            {
              title: "Data Processed",
              value: userData.stats.dataProcessed,
              icon: Database,
              color: "text-purple-600",
              bgColor: "bg-purple-50",
              suffix: "TB",
              decimals: 1,
            },
          ].map((stat, index) => (
            <Card key={index} className="bg-white/80 backdrop-blur-sm border-blue-100 hover:shadow-lg transition-all">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900">
                      <AnimatedCounter end={stat.value} suffix={stat.suffix} decimals={stat.decimals || 0} />
                    </p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.bgColor}`}>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Performance Metrics */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-600" />
              Performance Metrics
            </CardTitle>
            <CardDescription>AI system performance across key indicators</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Object.entries(userData.performance).map(([key, value]) => (
                <div key={key} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 capitalize">{key}</span>
                    <span className="text-sm font-bold text-gray-900">{value}%</span>
                  </div>
                  <Progress value={value} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Tabs Section */}
        <Tabs defaultValue="activities" className="space-y-6">
          {/* <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:grid-cols-3">
            <TabsTrigger value="activities" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Activities
            </TabsTrigger>
            <TabsTrigger value="interactions" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Interactions
            </TabsTrigger>
            <TabsTrigger value="achievements" className="flex items-center gap-2">
              <Award className="h-4 w-4" />
              Achievements
            </TabsTrigger>
          </TabsList> */}

          {/* <TabsContent value="activities">
            <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
              <CardHeader>
                <CardTitle>Recent Activities</CardTitle>
                <CardDescription>Latest AI tasks and operations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {userData.recentActivities.map((activity) => (
                    <ActivityItem key={activity.id} activity={activity} />
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent> */}

          {/* <TabsContent value="interactions">
            <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
              <CardHeader>
                <CardTitle>User Interactions</CardTitle>
                <CardDescription>Recent conversations and queries</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {userData.interactions.map((interaction) => (
                    <InteractionItem key={interaction.id} interaction={interaction} />
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent> */}

          {/* <TabsContent value="achievements">
            <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
              <CardHeader>
                <CardTitle>Achievements & Milestones</CardTitle>
                <CardDescription>AI performance badges and accomplishments</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {userData.achievements.map((achievement, index) => (
                    <AchievementBadge key={index} achievement={achievement} />
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent> */}
        </Tabs>

      </div>
    </div>
  )
}
