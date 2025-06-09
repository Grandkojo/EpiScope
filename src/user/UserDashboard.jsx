import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { LineChart } from "../components/charts/LineChart"
import { PieChart } from "../components/charts/PieChart"
import { StatCard } from "../components/dashboard/StatCard"
import { healthMetrics, monthlyTrends, ghanaRegions, hotspots } from "../data/dummyData"
import { Activity, HeartPulse, TrendingUp, Users, MapPin, AlertTriangle } from "lucide-react"
import { useState } from "react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select"

const UserDashboard = () => {
  const [selectedRegion, setSelectedRegion] = useState("Greater Accra")

  // Transform monthly trends data for the selected region
  const regionTrends = monthlyTrends.map(trend => ({
    month: trend.month,
    diabetes: Math.round(trend.diabetes * (selectedRegion === "All Regions" ? 1 : 0.15)),
    malaria: Math.round(trend.malaria * (selectedRegion === "All Regions" ? 1 : 0.15))
  }))

  // Disease distribution data
  const diseaseDistribution = [
    { name: "Diabetes", value: 35 },
    { name: "Malaria", value: 45 },
    { name: "Other", value: 20 }
  ]

  // Get hotspots for selected region
  const regionHotspots = selectedRegion === "All Regions" 
    ? hotspots 
    : hotspots.filter(hotspot => hotspot.region === selectedRegion)

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">My Health Dashboard</h1>
        <Select value={selectedRegion} onValueChange={setSelectedRegion}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select Region" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All Regions">All Regions</SelectItem>
            {ghanaRegions.map(region => (
              <SelectItem key={region} value={region}>{region}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Health Status"
          value="Good"
          description="Your current health status"
          icon={<HeartPulse className="h-4 w-4 text-green-500" />}
        />
        <StatCard
          title="Risk Level"
          value="Low"
          description="Based on your region"
          icon={<Activity className="h-4 w-4 text-blue-500" />}
        />
        <StatCard
          title="Monthly Cases"
          value={regionTrends[regionTrends.length - 1].diabetes}
          description="Diabetes cases in your region"
          icon={<TrendingUp className="h-4 w-4 text-orange-500" />}
        />
        <StatCard
          title="Population at Risk"
          value={Math.round(healthMetrics.populationAtRisk * (selectedRegion === "All Regions" ? 1 : 0.15))}
          description="In your region"
          icon={<Users className="h-4 w-4 text-purple-500" />}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Health Trends */}
        <Card>
          <CardHeader>
            <CardTitle>Health Trends in {selectedRegion}</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart
              data={regionTrends}
              categories={["diabetes", "malaria"]}
              index="month"
              colors={["#f97316", "#3b82f6"]}
              valueFormatter={(value) => `${value} cases`}
            />
          </CardContent>
        </Card>

        {/* Disease Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Disease Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <PieChart
              data={diseaseDistribution}
              colors={["#f97316", "#3b82f6", "#22c55e"]}
            />
          </CardContent>
        </Card>
      </div>

      {/* Hotspots */}
      <Card>
        <CardHeader>
          <CardTitle>Health Hotspots in {selectedRegion}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {regionHotspots.map((hotspot) => (
              <div
                key={hotspot.id}
                className="flex items-start space-x-4 p-4 rounded-lg border"
              >
                <div className="flex-shrink-0">
                  <AlertTriangle className={`h-5 w-5 ${
                    hotspot.severity === "high" ? "text-red-500" :
                    hotspot.severity === "medium" ? "text-yellow-500" :
                    "text-green-500"
                  }`} />
                </div>
                <div>
                  <h3 className="font-medium">{hotspot.region}</h3>
                  <p className="text-sm text-gray-500">
                    Diabetes Rate: {hotspot.diabetesRate}%
                  </p>
                  <p className="text-sm text-gray-500">
                    Malaria Rate: {hotspot.malariaRate}%
                  </p>
                  <p className="text-sm text-gray-500">
                    Severity: {hotspot.severity}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Health Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Health Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <HeartPulse className="h-5 w-5 text-red-500" />
              </div>
              <div>
                <h3 className="font-medium">Regular Check-ups</h3>
                <p className="text-sm text-gray-500">
                  Schedule regular health check-ups to monitor your condition.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <Activity className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <h3 className="font-medium">Stay Active</h3>
                <p className="text-sm text-gray-500">
                  Maintain regular physical activity to improve your health.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <TrendingUp className="h-5 w-5 text-green-500" />
              </div>
              <div>
                <h3 className="font-medium">Monitor Trends</h3>
                <p className="text-sm text-gray-500">
                  Keep track of health trends in your region to stay informed.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default UserDashboard 