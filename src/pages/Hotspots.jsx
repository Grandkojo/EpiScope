"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { MapPin, AlertTriangle, Users, Activity } from "lucide-react"
import { hotspots } from "../data/dummyData"

const Hotspots = () => {
  const [selectedHotspot, setSelectedHotspot] = useState(null)
  const [filterSeverity, setFilterSeverity] = useState("all")

  const filteredHotspots = hotspots.filter((hotspot) => filterSeverity === "all" || hotspot.severity === filterSeverity)

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "high":
        return "bg-red-500/20 text-red-400 border-red-500/30"
      case "medium":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
      case "low":
        return "bg-green-500/20 text-green-400 border-green-500/30"
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30"
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Disease Hotspots</h1>
          <p className="text-muted-foreground">Geographic distribution of health risks</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-health-500"
          >
            <option value="all">All Severities</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
        </div>
      </div>

      {/* Map Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="h-5 w-5 text-health-400" />
            <span>Ghana Health Risk Map</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative h-96 bg-gradient-to-br from-green-900/20 to-green-800/10 rounded-lg border border-border overflow-hidden">
            {/* Map Background */}
            <div className="absolute inset-0 bg-texture opacity-20"></div>

            {/* Hotspot Markers */}
            {filteredHotspots.map((hotspot) => (
              <div
                key={hotspot.id}
                className={`absolute w-4 h-4 rounded-full cursor-pointer transition-all duration-200 hover:scale-150 ${
                  hotspot.severity === "high"
                    ? "bg-red-500"
                    : hotspot.severity === "medium"
                      ? "bg-yellow-500"
                      : "bg-green-500"
                }`}
                style={{
                  left: `${(hotspot.lng + 3) * 15 + 20}%`,
                  top: `${(11 - hotspot.lat) * 8 + 10}%`,
                }}
                onClick={() => setSelectedHotspot(hotspot)}
              >
                <div className="absolute inset-0 rounded-full animate-ping opacity-75"></div>
              </div>
            ))}

            {/* Map Labels */}
            <div className="absolute top-4 left-4 text-sm text-muted-foreground">
              <p>Ghana Health Hotspots</p>
              <p className="text-xs">Click markers for details</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hotspots Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredHotspots.map((hotspot) => (
          <Card
            key={hotspot.id}
            className={`cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105 ${
              selectedHotspot?.id === hotspot.id ? "ring-2 ring-health-500" : ""
            }`}
            onClick={() => setSelectedHotspot(hotspot)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{hotspot.region}</CardTitle>
                <div
                  className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(hotspot.severity)}`}
                >
                  {hotspot.severity.toUpperCase()}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-red-400" />
                  <div>
                    <p className="text-xs text-muted-foreground">Malaria Rate</p>
                    <p className="font-semibold">{hotspot.malariaRate.toFixed(1)}%</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-health-400" />
                  <div>
                    <p className="text-xs text-muted-foreground">Diabetes Rate</p>
                    <p className="font-semibold">{hotspot.diabetesRate.toFixed(1)}%</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Users className="h-4 w-4 text-blue-400" />
                <div>
                  <p className="text-xs text-muted-foreground">Population</p>
                  <p className="font-semibold">{hotspot.population.toLocaleString()}</p>
                </div>
              </div>

              <div className="pt-2 border-t border-border">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Risk Level</span>
                  <span className="flex items-center space-x-1">
                    <AlertTriangle className="h-3 w-3" />
                    <span>{hotspot.severity}</span>
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Selected Hotspot Details */}
      {selectedHotspot && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="h-5 w-5 text-health-400" />
              <span>{selectedHotspot.region} - Detailed Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h3 className="font-semibold text-foreground">Geographic Info</h3>
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="text-muted-foreground">Latitude:</span> {selectedHotspot.lat}
                  </p>
                  <p>
                    <span className="text-muted-foreground">Longitude:</span> {selectedHotspot.lng}
                  </p>
                  <p>
                    <span className="text-muted-foreground">Population:</span>{" "}
                    {selectedHotspot.population.toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold text-foreground">Disease Rates</h3>
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="text-muted-foreground">Malaria:</span> {selectedHotspot.malariaRate.toFixed(2)}%
                  </p>
                  <p>
                    <span className="text-muted-foreground">Diabetes:</span> {selectedHotspot.diabetesRate.toFixed(2)}%
                  </p>
                  <p>
                    <span className="text-muted-foreground">Risk Level:</span> {selectedHotspot.severity}
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold text-foreground">Recommendations</h3>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>• Increase healthcare facilities</p>
                  <p>• Implement prevention programs</p>
                  <p>• Monitor disease progression</p>
                  <p>• Community health education</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Hotspots
