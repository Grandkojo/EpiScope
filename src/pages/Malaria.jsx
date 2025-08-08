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
  PieChart,
  Pie,
  Cell,
} from "recharts"
import { Droplets, TrendingDown, Shield, Thermometer, Calendar, Download } from "lucide-react"
import { malariaData } from "../data/dummyData"
import MetricCard from "../components/MetricCard"

const Malaria = () => {
  const [selectedSeason, setSelectedSeason] = useState("all")

  // Enhanced malaria data
  const malariaSeasonality = [
    { month: "Jan", cases: 45230, rainfall: 12, temperature: 28 },
    { month: "Feb", cases: 38940, rainfall: 8, temperature: 31 },
    { month: "Mar", cases: 52340, rainfall: 45, temperature: 32 },
    { month: "Apr", cases: 67890, rainfall: 78, temperature: 30 },
    { month: "May", cases: 89670, rainfall: 125, temperature: 29 },
    { month: "Jun", cases: 123450, rainfall: 180, temperature: 27 },
    { month: "Jul", cases: 145670, rainfall: 220, temperature: 26 },
    { month: "Aug", cases: 134560, rainfall: 195, temperature: 26 },
    { month: "Sep", cases: 98760, rainfall: 165, temperature: 27 },
    { month: "Oct", cases: 76540, rainfall: 98, temperature: 29 },
    { month: "Nov", cases: 54320, rainfall: 35, temperature: 30 },
    { month: "Dec", cases: 43210, rainfall: 18, temperature: 29 },
  ]

  const malariaAgeGroups = [
    { ageGroup: "Under 5", cases: 234560, percentage: 38.3, mortality: 12.4 },
    { ageGroup: "5-14", cases: 156780, percentage: 25.6, mortality: 3.2 },
    { ageGroup: "15-29", cases: 98760, percentage: 16.1, mortality: 1.8 },
    { ageGroup: "30-49", cases: 76540, percentage: 12.5, mortality: 2.1 },
    { ageGroup: "50+", cases: 45250, percentage: 7.4, mortality: 8.7 },
  ]

  const preventionMethods = [
    { method: "Bed Nets", coverage: 78.5, effectiveness: 85 },
    { method: "Indoor Spraying", coverage: 45.2, effectiveness: 92 },
    { method: "Antimalarial Drugs", coverage: 67.8, effectiveness: 88 },
    { method: "Environmental Management", coverage: 34.6, effectiveness: 75 },
    { method: "Community Education", coverage: 82.1, effectiveness: 65 },
  ]

  const COLORS = ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6", "#8b5cf6"]

  const totalMalariaCases = malariaData.reduce((sum, region) => sum + region.cases, 0)
  const averageRate = malariaData.reduce((sum, region) => sum + region.rate, 0) / malariaData.length
  const highRiskRegions = malariaData.filter((region) => region.rate > 30).length

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center space-x-3">
            <Droplets className="h-8 w-8 text-blue-400" />
            <span>Malaria Control</span>
          </h1>
          <p className="text-muted-foreground">Comprehensive malaria surveillance and prevention tracking</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="secondary" size="sm">
            <Shield className="h-4 w-4 mr-2" />
            Prevention
          </Button>
          <Button variant="secondary" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Cases"
          value={totalMalariaCases.toLocaleString()}
          change={-4.7}
          icon={Droplets}
          trend="down"
          color="danger"
        />
        <MetricCard
          title="Average Rate"
          value={`${averageRate.toFixed(1)}%`}
          change={-2.1}
          icon={TrendingDown}
          trend="down"
          color="health"
        />
        <MetricCard title="High Risk Regions" value={highRiskRegions} icon={Thermometer} color="warning" />
        <MetricCard title="Prevention Coverage" value="78.5%" change={8.3} icon={Shield} trend="up" color="health" />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Seasonal Patterns */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-health-400" />
              <span>Seasonal Patterns</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={malariaSeasonality}>
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
                <Bar yAxisId="left" dataKey="cases" fill="#3b82f6" name="Malaria Cases" />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="rainfall"
                  stroke="#22c55e"
                  strokeWidth={3}
                  name="Rainfall (mm)"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Age Group Distribution */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
          <CardHeader>
            <CardTitle>Age Group Impact</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={malariaAgeGroups}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="cases"
                  label={({ ageGroup, percentage }) => `${ageGroup}: ${percentage}%`}
                >
                  {malariaAgeGroups.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1f2937",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Prevention Methods */}
      <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5 text-health-400" />
            <span>Prevention Methods Effectiveness</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {preventionMethods.map((method, index) => (
              <div
                key={index}
                className="p-4 rounded-lg border border-border bg-card/50 hover:bg-card/80 transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-foreground">{method.method}</h3>
                  <span className="text-xs text-muted-foreground">{method.effectiveness}% effective</span>
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-muted-foreground">Coverage</span>
                      <span className="font-medium">{method.coverage}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div className="h-2 rounded-full bg-blue-500" style={{ width: `${method.coverage}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-muted-foreground">Effectiveness</span>
                      <span className="font-medium">{method.effectiveness}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-green-500"
                        style={{ width: `${method.effectiveness}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Regional Malaria Rates */}
      <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle>Regional Malaria Burden</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={malariaData}>
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
              <Bar dataKey="rate" fill="#3b82f6" name="Malaria Rate (%)" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Mortality by Age Group */}
      <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle>Mortality Rates by Age Group</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {malariaAgeGroups.map((group, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-card/50">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  ></div>
                  <span className="font-medium">{group.ageGroup}</span>
                </div>
                <div className="flex items-center space-x-6 text-sm">
                  <div className="text-center">
                    <p className="text-muted-foreground">Cases</p>
                    <p className="font-semibold">{group.cases.toLocaleString()}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-muted-foreground">Mortality</p>
                    <p className="font-semibold text-red-400">{group.mortality}%</p>
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

export default Malaria
