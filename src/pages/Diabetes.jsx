// "use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import {
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
  Area,
  AreaChart,
} from "recharts"
import { Heart, TrendingUp, Users, AlertCircle, Calendar, Filter } from "lucide-react"
import { diabetesData } from "../data/dummyData"
import MetricCard from "../components/MetricCard"

const Diabetes = () => {
  const [selectedRegion, setSelectedRegion] = useState("all")
  const [timeRange, setTimeRange] = useState("12months")

  // Enhanced diabetes data with age groups and risk factors
  const diabetesAgeGroups = [
    { ageGroup: "18-29", cases: 8420, percentage: 9.5, risk: "low" },
    { ageGroup: "30-39", cases: 15680, percentage: 17.7, risk: "medium" },
    { ageGroup: "40-49", cases: 22340, percentage: 25.2, risk: "medium" },
    { ageGroup: "50-59", cases: 24890, percentage: 28.1, risk: "high" },
    { ageGroup: "60+", cases: 17430, percentage: 19.6, risk: "high" },
  ]

  const diabetesRiskFactors = [
    { factor: "Obesity", prevalence: 34.2, impact: "high" },
    { factor: "Sedentary Lifestyle", prevalence: 45.8, impact: "high" },
    { factor: "Family History", prevalence: 28.6, impact: "medium" },
    { factor: "Hypertension", prevalence: 31.4, impact: "high" },
    { factor: "Poor Diet", prevalence: 52.3, impact: "medium" },
    { factor: "Stress", prevalence: 38.7, impact: "medium" },
  ]

  const diabetesProgression = [
    { month: "Jan", newCases: 6420, totalCases: 77890, mortality: 234, recovery: 1240 },
    { month: "Feb", newCases: 6890, totalCases: 84780, mortality: 267, recovery: 1180 },
    { month: "Mar", newCases: 7230, totalCases: 92010, mortality: 289, recovery: 1320 },
    { month: "Apr", newCases: 6780, totalCases: 98790, mortality: 245, recovery: 1450 },
    { month: "May", newCases: 7450, totalCases: 106240, mortality: 298, recovery: 1380 },
    { month: "Jun", newCases: 7890, totalCases: 114130, mortality: 312, recovery: 1520 },
  ]

  const totalDiabetesCases = diabetesData.reduce((sum, region) => sum + region.cases, 0)
  const averageRate = diabetesData.reduce((sum, region) => sum + region.rate, 0) / diabetesData.length
  const highRiskRegions = diabetesData.filter((region) => region.rate > 3.5).length

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center space-x-3">
            <Heart className="h-8 w-8 text-red-400" />
            <span>Diabetes Monitoring</span>
          </h1>
          <p className="text-muted-foreground">Comprehensive diabetes tracking and analysis for Ghana</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="secondary" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter Data
          </Button>
          <Button variant="secondary" size="sm">
            <Calendar className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Cases"
          value={totalDiabetesCases.toLocaleString()}
          change={2.3}
          icon={Heart}
          trend="up"
          color="danger"
        />
        <MetricCard
          title="Average Rate"
          value={`${averageRate.toFixed(1)}%`}
          change={0.8}
          icon={TrendingUp}
          trend="up"
          color="warning"
        />
        <MetricCard title="High Risk Regions" value={highRiskRegions} icon={AlertCircle} color="danger" />
        <MetricCard title="Population Screened" value="2.4M" change={12.5} icon={Users} trend="up" color="health" />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Disease Progression */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-health-400" />
              <span>Diabetes Progression</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={diabetesProgression}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="month" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1f2937",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                  }}
                />
                <Bar dataKey="newCases" fill="#ef4444" name="New Cases" />
                <Line type="monotone" dataKey="totalCases" stroke="#22c55e" strokeWidth={3} name="Total Cases" />
              </ComposedChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Age Group Distribution */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
          <CardHeader>
            <CardTitle>Age Group Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={diabetesAgeGroups} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9ca3af" />
                <YAxis dataKey="ageGroup" type="category" stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1f2937",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                  }}
                />
                <Bar dataKey="cases" fill="#f59e0b" name="Cases" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Risk Factors Analysis */}
      <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-health-400" />
            <span>Risk Factors Analysis</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {diabetesRiskFactors.map((factor, index) => (
              <div
                key={index}
                className="p-4 rounded-lg border border-border bg-card/50 hover:bg-card/80 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-foreground">{factor.factor}</h3>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      factor.impact === "high"
                        ? "bg-red-500/20 text-red-400"
                        : factor.impact === "medium"
                          ? "bg-yellow-500/20 text-yellow-400"
                          : "bg-green-500/20 text-green-400"
                    }`}
                  >
                    {factor.impact}
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Prevalence</span>
                    <span className="font-medium">{factor.prevalence}%</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        factor.impact === "high"
                          ? "bg-red-500"
                          : factor.impact === "medium"
                            ? "bg-yellow-500"
                            : "bg-green-500"
                      }`}
                      style={{ width: `${factor.prevalence}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Regional Breakdown */}
      <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle>Regional Diabetes Rates</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={diabetesData}>
              <defs>
                <linearGradient id="diabetesAreaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="region" stroke="#9ca3af" angle={-45} textAnchor="end" height={100} />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                }}
              />
              <Area
                type="monotone"
                dataKey="rate"
                stroke="#ef4444"
                fillOpacity={1}
                fill="url(#diabetesAreaGradient)"
                name="Diabetes Rate (%)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}

export default Diabetes
