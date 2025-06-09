import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import MetricCard from "../components/MetricCard"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts"
import { Heart, Droplets, MapPin, Users, TrendingUp, AlertTriangle } from "lucide-react"
import { healthMetrics, monthlyTrends, diabetesData, malariaData } from "../data/dummyData"

const Dashboard = () => {
  const COLORS = ["#22c55e", "#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6"]

  const diseaseDistribution = [
    { name: "Malaria", value: healthMetrics.totalMalariaCases, color: "#ef4444" },
    { name: "Diabetes", value: healthMetrics.totalDiabetesCases, color: "#22c55e" },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Health Dashboard</h1>
          <p className="text-gray-500">Ghana Disease Monitoring & Analytics</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse"></div>
          <span>Live Data</span>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Diabetes Cases"
          value={healthMetrics.totalDiabetesCases.toLocaleString()}
          change={healthMetrics.monthlyGrowthDiabetes}
          icon={Heart}
          trend="up"
          color="health"
        />
        <MetricCard
          title="Total Malaria Cases"
          value={healthMetrics.totalMalariaCases.toLocaleString()}
          change={Math.abs(healthMetrics.monthlyGrowthMalaria)}
          icon={Droplets}
          trend="down"
          color="danger"
        />
        <MetricCard title="Critical Hotspots" value={healthMetrics.criticalHotspots} icon={MapPin} color="warning" />
        <MetricCard
          title="Population at Risk"
          value={`${(healthMetrics.populationAtRisk / 1000000).toFixed(1)}M`}
          icon={Users}
          color="info"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Trends */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-health-400" />
              <span>Monthly Disease Trends</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyTrends}>
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
                <Line type="monotone" dataKey="diabetes" stroke="#22c55e" strokeWidth={3} name="Diabetes" />
                <Line type="monotone" dataKey="malaria" stroke="#ef4444" strokeWidth={3} name="Malaria" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Disease Distribution */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-health-400" />
              <span>Disease Distribution</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={diseaseDistribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {diseaseDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
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

      {/* Regional Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart className="h-5 w-5 text-health-400" />
            <span>Regional Disease Rates (per 1000 population)</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={diabetesData.map((item, index) => ({
                ...item,
                malariaRate: malariaData[index]?.rate || 0,
              }))}
            >
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
              <Legend />
              <Bar dataKey="rate" fill="#22c55e" name="Diabetes Rate" />
              <Bar dataKey="malariaRate" fill="#ef4444" name="Malaria Rate" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard
