// "use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
  Bar,
  RadialBarChart,
  RadialBar,
  Legend,
} from "recharts"
import { Activity, TrendingUp, Calendar, BarChart3, Target, Zap } from "lucide-react"

const Trends = () => {
  const [selectedMetric, setSelectedMetric] = useState("both")
  const [timeframe, setTimeframe] = useState("12months")

  // Enhanced trend data
  const yearlyComparison = [
    { year: "2020", diabetes: 72340, malaria: 890450, population: 30417856 },
    { year: "2021", diabetes: 75680, malaria: 823670, population: 31072940 },
    { year: "2022", diabetes: 79120, malaria: 756890, population: 31732129 },
    { year: "2023", diabetes: 82890, malaria: 698760, population: 32395450 },
    { year: "2024", diabetes: 88760, malaria: 612890, population: 33072840 },
  ]

  const predictiveData = [
    { month: "Jan 2024", actual: 88760, predicted: 89200, confidence: 95 },
    { month: "Feb 2024", actual: 91340, predicted: 91800, confidence: 93 },
    { month: "Mar 2024", actual: 94230, predicted: 94100, confidence: 91 },
    { month: "Apr 2024", actual: null, predicted: 96500, confidence: 88 },
    { month: "May 2024", actual: null, predicted: 98200, confidence: 85 },
    { month: "Jun 2024", actual: null, predicted: 99800, confidence: 82 },
  ]

  const healthIndicators = [
    { indicator: "Healthcare Access", current: 68, target: 85, progress: 80 },
    { indicator: "Prevention Coverage", current: 72, target: 90, progress: 80 },
    { indicator: "Early Detection", current: 45, target: 75, progress: 60 },
    { indicator: "Treatment Success", current: 78, target: 95, progress: 82 },
    { indicator: "Community Awareness", current: 62, target: 80, progress: 78 },
  ]

  const seasonalPatterns = [
    { month: "Jan", diabetes: 2.8, malaria: 15.2, rainfall: 12, temperature: 28 },
    { month: "Feb", diabetes: 2.9, malaria: 12.8, rainfall: 8, temperature: 31 },
    { month: "Mar", diabetes: 3.1, malaria: 18.4, rainfall: 45, temperature: 32 },
    { month: "Apr", diabetes: 3.0, malaria: 24.6, rainfall: 78, temperature: 30 },
    { month: "May", diabetes: 3.2, malaria: 32.1, rainfall: 125, temperature: 29 },
    { month: "Jun", diabetes: 3.3, malaria: 42.8, rainfall: 180, temperature: 27 },
    { month: "Jul", diabetes: 3.4, malaria: 48.9, rainfall: 220, temperature: 26 },
    { month: "Aug", diabetes: 3.3, malaria: 45.2, rainfall: 195, temperature: 26 },
    { month: "Sep", diabetes: 3.2, malaria: 36.7, rainfall: 165, temperature: 27 },
    { month: "Oct", diabetes: 3.1, malaria: 28.4, rainfall: 98, temperature: 29 },
    { month: "Nov", diabetes: 2.9, malaria: 21.6, rainfall: 35, temperature: 30 },
    { month: "Dec", diabetes: 2.8, malaria: 18.3, rainfall: 18, temperature: 29 },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center space-x-3">
            <Activity className="h-8 w-8 text-health-400" />
            <span>Health Trends</span>
          </h1>
          <p className="text-muted-foreground">Advanced trend analysis and predictive insights</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500"
          >
            <option value="both">Both Diseases</option>
            <option value="diabetes">Diabetes Only</option>
            <option value="malaria">Malaria Only</option>
          </select>
          <Button variant="secondary" size="sm">
            <Calendar className="h-4 w-4 mr-2" />
            Time Range
          </Button>
        </div>
      </div>

      {/* Yearly Comparison */}
      <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-health-400" />
            <span>5-Year Disease Trends</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={yearlyComparison}>
              <defs>
                <linearGradient id="diabetesYearlyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="malariaYearlyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="year" stroke="#9ca3af" />
              <YAxis yAxisId="left" stroke="#9ca3af" />
              <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                }}
              />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="diabetes"
                stroke="#22c55e"
                fillOpacity={1}
                fill="url(#diabetesYearlyGradient)"
                name="Diabetes Cases"
              />
              <Area
                yAxisId="right"
                type="monotone"
                dataKey="malaria"
                stroke="#ef4444"
                fillOpacity={1}
                fill="url(#malariaYearlyGradient)"
                name="Malaria Cases"
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="population"
                stroke="#3b82f6"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Population"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Predictive Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-health-400" />
              <span>Predictive Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={predictiveData}>
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
                <Line
                  type="monotone"
                  dataKey="actual"
                  stroke="#22c55e"
                  strokeWidth={3}
                  name="Actual Cases"
                  connectNulls={false}
                />
                <Line
                  type="monotone"
                  dataKey="predicted"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Predicted Cases"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Health Indicators Progress */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-health-400" />
              <span>Health Indicators Progress</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RadialBarChart cx="50%" cy="50%" innerRadius="20%" outerRadius="90%" data={healthIndicators}>
                <RadialBar
                  minAngle={15}
                  label={{ position: "insideStart", fill: "#fff" }}
                  background
                  clockWise
                  dataKey="progress"
                  fill="#22c55e"
                />
                <Legend iconSize={10} layout="vertical" verticalAlign="middle" align="right" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1f2937",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                  }}
                />
              </RadialBarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Seasonal Correlation */}
      <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-health-400" />
            <span>Seasonal Disease Patterns</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={seasonalPatterns}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="month" stroke="#9ca3af" />
              <YAxis yAxisId="left" stroke="#9ca3af" />
              <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                }}
              />
              <Bar yAxisId="left" dataKey="rainfall" fill="#3b82f6" name="Rainfall (mm)" opacity={0.6} />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="diabetes"
                stroke="#22c55e"
                strokeWidth={3}
                name="Diabetes Rate (%)"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="malaria"
                stroke="#ef4444"
                strokeWidth={3}
                name="Malaria Rate (%)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Health Indicators Detail */}
      <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle>Health System Performance Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {healthIndicators.map((indicator, index) => (
              <div key={index} className="p-4 rounded-lg border border-border bg-card/50">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-foreground">{indicator.indicator}</h3>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-muted-foreground">
                      Current: <span className="font-medium text-foreground">{indicator.current}%</span>
                    </span>
                    <span className="text-muted-foreground">
                      Target: <span className="font-medium text-health-400">{indicator.target}%</span>
                    </span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Progress</span>
                    <span>{indicator.progress}%</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div className="h-2 rounded-full bg-health-500" style={{ width: `${indicator.progress}%` }}></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Trends
