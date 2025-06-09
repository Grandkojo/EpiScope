"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts"
import { BarChart3, Filter, Download, Calendar } from "lucide-react"
import { monthlyTrends, diabetesData, malariaData } from "../data/dummyData"

const Analytics = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState("12months")

  const correlationData = diabetesData.map((item, index) => ({
    region: item.region,
    diabetes: item.rate,
    malaria: malariaData[index]?.rate || 0,
    population: item.population / 1000000,
  }))

  const radarData = [
    { subject: "Incidence Rate", diabetes: 3.2, malaria: 28.5, fullMark: 50 },
    { subject: "Mortality Rate", diabetes: 0.8, malaria: 12.3, fullMark: 20 },
    { subject: "Treatment Success", diabetes: 85, malaria: 92, fullMark: 100 },
    { subject: "Prevention Coverage", diabetes: 65, malaria: 78, fullMark: 100 },
    { subject: "Healthcare Access", diabetes: 72, malaria: 68, fullMark: 100 },
    { subject: "Public Awareness", diabetes: 58, malaria: 82, fullMark: 100 },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Advanced Analytics</h1>
          <p className="text-muted-foreground">Deep insights into health data patterns</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="secondary" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button variant="secondary" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Time Range Selector */}
      <div className="flex items-center space-x-4">
        <Calendar className="h-5 w-5 text-muted-foreground" />
        <div className="flex space-x-2">
          {["3months", "6months", "12months", "2years"].map((period) => (
            <Button
              key={period}
              variant={selectedTimeframe === period ? "default" : "secondary"}
              size="sm"
              onClick={() => setSelectedTimeframe(period)}
            >
              {period.replace("months", "M").replace("years", "Y")}
            </Button>
          ))}
        </div>
      </div>

      {/* Advanced Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trend Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-health-400" />
              <span>Disease Trend Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={monthlyTrends}>
                <defs>
                  <linearGradient id="diabetesGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0.1} />
                  </linearGradient>
                  <linearGradient id="malariaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
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
                <Area
                  type="monotone"
                  dataKey="diabetes"
                  stroke="#22c55e"
                  fillOpacity={1}
                  fill="url(#diabetesGradient)"
                  name="Diabetes"
                />
                <Area
                  type="monotone"
                  dataKey="malaria"
                  stroke="#ef4444"
                  fillOpacity={1}
                  fill="url(#malariaGradient)"
                  name="Malaria"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Correlation Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Disease Correlation by Region</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart data={correlationData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" dataKey="diabetes" name="Diabetes Rate" stroke="#9ca3af" />
                <YAxis type="number" dataKey="malaria" name="Malaria Rate" stroke="#9ca3af" />
                <Tooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  contentStyle={{
                    backgroundColor: "#1f2937",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                  }}
                  formatter={(value, name) => [value.toFixed(2), name]}
                />
                <Scatter dataKey="population" fill="#22c55e" name="Population (M)" />
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Comprehensive Health Radar */}
      <Card>
        <CardHeader>
          <CardTitle>Comprehensive Health Assessment</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#374151" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: "#9ca3af", fontSize: 12 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "#9ca3af", fontSize: 10 }} />
              <Radar
                name="Diabetes"
                dataKey="diabetes"
                stroke="#22c55e"
                fill="#22c55e"
                fillOpacity={0.2}
                strokeWidth={2}
              />
              <Radar
                name="Malaria"
                dataKey="malaria"
                stroke="#ef4444"
                fill="#ef4444"
                fillOpacity={0.2}
                strokeWidth={2}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}

export default Analytics
