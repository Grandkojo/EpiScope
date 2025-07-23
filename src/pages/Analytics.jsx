import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "../components/ui/select"
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
  ReferenceDot,
  BarChart,
  PieChart,
  Pie,
  LineChart,
  Line,
  Legend,
  Bar,
} from "recharts"
import {
  BarChart3,
  Filter,
  Download,
  Calendar,
  RefreshCw,
  Activity,
  TrendingUp,
  Users,
  AlertCircle,
} from "lucide-react"
import { monthlyTrends, diabetesData, malariaData } from "../data/dummyData"

// Dummy disease meta
const DISEASES = [
  {
    key: "diabetes",
    label: "Diabetes",
    color: "#22c55e",
    stats: { incidence: 90, mortality: 5, description: "Chronic high blood sugar." },
  },
  {
    key: "malaria",
    label: "Malaria",
    color: "#ef4444",
    stats: { incidence: 12, mortality: 1, description: "Mosquito-borne infection." },
  },
  {
    key: "all",
    label: "All Diseases",
    color: "#6366f1",
    stats: { incidence: 51, mortality: 3, description: "Aggregate of all diseases." },
  },
]

// Dummy radar metrics
const RADAR_METRICS = [
  "Incidence Rate",
  "Mortality Rate",
  "Treatment Success",
  "Prevention Coverage",
  "Healthcare Access",
  "Public Awareness",
]

const getDiseaseMeta = (key) => DISEASES.find((d) => d.key === key) || DISEASES[0]

const getTrendData = (d1, d2, data) => {
  // For "all", average the values
  if (d1 === "all" && d2 === "all") return data
  return data.map((row) => ({
    ...row,
    d1: d1 === "all" ? (row.diabetes + row.malaria) / 2 : row[d1],
    d2: d2 === "all" ? (row.diabetes + row.malaria) / 2 : row[d2],
  }))
}

const getPercentChange = (arr, idx, key) => {
  if (idx <= 0 || !arr[idx - 1] || arr[idx - 1][key] === undefined) return null
  const prev = arr[idx - 1][key]
  const curr = arr[idx][key]
  if (!prev) return null
  return (((curr - prev) / prev) * 100).toFixed(1)
}

const lastUpdated = "2024-06-01"

// Dummy data for new analytics (replace with real data as needed)
const HOTSPOTS = [
  { locality: "MADINA-NEW RD", disease: "Diabetes", cases: 120, population: 5000 },
  { locality: "GBAWE, TELECOM", disease: "Diabetes", cases: 90, population: 4000 },
  { locality: "KWASHIEMAN", disease: "Malaria", cases: 200, population: 6000 },
  { locality: "UPPER-WEIJA", disease: "Malaria", cases: 150, population: 4500 },
]
const AGE_DISTRIBUTION = [
  { age: "0-18", cases: 30 },
  { age: "19-35", cases: 80 },
  { age: "36-60", cases: 150 },
  { age: "60+", cases: 100 },
]
const SEX_DISTRIBUTION = [
  { sex: "Male", cases: 180 },
  { sex: "Female", cases: 180 },
]
const PRINCIPAL_DIAGNOSES = [
  { diagnosis: "E08.40", count: 60 },
  { diagnosis: "E11.65", count: 45 },
  { diagnosis: "B50.9", count: 120 },
  { diagnosis: "E13.621", count: 30 },
]
const ADDITIONAL_DIAGNOSES = [
  { diagnosis: "R73.9", count: 20 },
  { diagnosis: "L30.3", count: 10 },
  { diagnosis: "N34.1", count: 15 },
]
const NHIA_STATUS = [
  { status: "NHIA", count: 250 },
  { status: "Non-NHIA", count: 110 },
]
const PREGNANCY_STATUS = [
  { status: "Pregnant", count: 20 },
  { status: "Not Pregnant", count: 340 },
]
const TRENDS_BY_LOCALITY = [
  { month: "Jan", "MADINA-NEW RD": 10, "GBAWE, TELECOM": 8, "KWASHIEMAN": 20 },
  { month: "Feb", "MADINA-NEW RD": 12, "GBAWE, TELECOM": 9, "KWASHIEMAN": 22 },
  { month: "Mar", "MADINA-NEW RD": 15, "GBAWE, TELECOM": 10, "KWASHIEMAN": 25 },
  { month: "Apr", "MADINA-NEW RD": 13, "GBAWE, TELECOM": 11, "KWASHIEMAN": 23 },
]

const Analytics = () => {
  // Disease dropdowns
  const [disease1, setDisease1] = useState("diabetes")
  const [disease2, setDisease2] = useState("malaria")

  // Chart mode
  const [chartMode, setChartMode] = useState("overlay") // or "side"

  // Date range (dummy)
  const [dateRange, setDateRange] = useState({ from: "2023-01", to: "2024-12" })

  // Forecast toggle
  const [showForecast, setShowForecast] = useState(false)

  // Radar controls
  const [radarMetrics, setRadarMetrics] = useState([...RADAR_METRICS])
  const [compareRadar, setCompareRadar] = useState(false)

  // Loading/empty state (dummy)
  const [loading, setLoading] = useState(false)
  const [empty, setEmpty] = useState(false)

  // Prepare trend data
  const trendData = getTrendData(disease1, disease2, monthlyTrends)

  // Dummy forecast data (extend by 2 months)
  const forecastData = showForecast
    ? [
        ...trendData,
        { month: "Jan+", d1: trendData[trendData.length - 1].d1 * 1.03, d2: trendData[trendData.length - 1].d2 * 1.02 },
        { month: "Feb+", d1: trendData[trendData.length - 1].d1 * 1.06, d2: trendData[trendData.length - 1].d2 * 1.04 },
      ]
    : trendData

  // Dummy annotation
  const annotationMonth = "Jun"

  // Radar data (dummy, filter metrics)
  const baseRadar = [
    { subject: "Incidence Rate", diabetes: 3.2, malaria: 28.5, fullMark: 50 },
    { subject: "Mortality Rate", diabetes: 0.8, malaria: 12.3, fullMark: 20 },
    { subject: "Treatment Success", diabetes: 85, malaria: 92, fullMark: 100 },
    { subject: "Prevention Coverage", diabetes: 65, malaria: 78, fullMark: 100 },
    { subject: "Healthcare Access", diabetes: 72, malaria: 68, fullMark: 100 },
    { subject: "Public Awareness", diabetes: 58, malaria: 82, fullMark: 100 },
  ]

  const radarData = baseRadar.filter((m) => radarMetrics.includes(m.subject))
  const radarCompare = compareRadar
    ? radarData.map((m) => ({ ...m, diabetes: m.diabetes * 0.95, malaria: m.malaria * 0.97 }))
    : null

  // Info box for disease
  const DiseaseInfoBox = ({ disease }) => {
    const meta = getDiseaseMeta(disease)
    return (
      <div className="flex items-center space-x-3 bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200 rounded-lg px-4 py-2.5 text-sm shadow-sm hover:shadow-md transition-shadow duration-200">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: meta.color }} />
          <span className="font-semibold text-slate-700">{meta.label}</span>
        </div>
        <div className="flex items-center space-x-3 text-slate-600">
          <div className="flex items-center space-x-1">
            <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
            <span className="text-xs">Incidence:</span>
            <span className="font-bold text-slate-800">{meta.stats.incidence}</span>
          </div>
          <div className="flex items-center space-x-1">
            <AlertCircle className="h-3.5 w-3.5 text-red-500" />
            <span className="text-xs">Mortality:</span>
            <span className="font-bold text-slate-800">{meta.stats.mortality}</span>
          </div>
        </div>
        <span className="text-slate-500 text-xs hidden lg:inline border-l border-slate-300 pl-3">
          {meta.stats.description}
        </span>
      </div>
    )
  }

  // Radar metric toggle
  const RadarMetricToggle = ({ metric }) => (
    <label className="flex items-center space-x-2 text-sm cursor-pointer hover:bg-slate-50 px-2 py-1 rounded transition-colors duration-150">
      <input
        type="checkbox"
        checked={radarMetrics.includes(metric)}
        onChange={(e) => {
          setRadarMetrics(e.target.checked ? [...radarMetrics, metric] : radarMetrics.filter((m) => m !== metric))
        }}
        className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 focus:ring-2"
      />
      <span className="text-slate-700">{metric}</span>
    </label>
  )

  // Loading/empty state
  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 w-1/3 bg-slate-200 rounded-lg mb-4" />
          <div className="h-64 bg-slate-100 rounded-xl" />
        </div>
      </div>
    )
  }

  if (empty) {
    return (
      <div className="p-8 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="h-8 w-8 text-slate-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-700 mb-2">No Data Available</h3>
          <p className="text-slate-500">No data available for this selection. Try adjusting your filters.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      <div className="p-6 lg:p-8 space-y-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="space-y-2">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <BarChart3 className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-3xl lg:text-4xl font-bold text-slate-800 tracking-tight">Advanced Analytics</h1>
                <p className="text-slate-600 text-lg">Deep insights into health data patterns</p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center space-x-2 bg-blue-50 border border-blue-200 px-3 py-2 rounded-lg">
              <Users className="h-4 w-4 text-blue-600" />
              <span className="text-blue-700 font-semibold text-sm">Weija Hospital Data</span>
            </div>
            <span className="text-sm text-slate-500 bg-slate-100 px-3 py-2 rounded-lg">
              Last updated: {lastUpdated}
            </span>
            <Button variant="outline" size="sm" className="shadow-sm hover:shadow-md transition-shadow bg-transparent">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
            <Button variant="outline" size="sm" className="shadow-sm hover:shadow-md transition-shadow bg-transparent">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Time Range Selector */}
        <Card className="shadow-sm border-slate-200">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-6">
              <div className="flex items-center space-x-3">
                <Calendar className="h-5 w-5 text-slate-500" />
                <span className="font-medium text-slate-700">Time Range:</span>
              </div>

              <div className="flex flex-wrap gap-2">
                {["3months", "6months", "12months", "2years"].map((period) => (
                  <Button
                    key={period}
                    variant={dateRange === period ? "default" : "outline"}
                    size="sm"
                    onClick={() => setDateRange(period)}
                    className="shadow-sm hover:shadow-md transition-all duration-200"
                  >
                    {period.replace("months", "M").replace("years", "Y")}
                  </Button>
                ))}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => alert("Custom date range picker coming soon!")}
                className="shadow-sm hover:shadow-md transition-shadow"
              >
                <Calendar className="h-4 w-4 mr-2" />
                Custom Range
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Disease Comparison Controls */}
        <Card className="shadow-sm border-slate-200">
          <CardContent className="p-6 space-y-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
              <div className="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
                <div className="flex items-center space-x-3">
                  <span className="font-medium text-slate-700">Compare:</span>
                  <Select value={disease1} onValueChange={setDisease1}>
                    <SelectTrigger className="w-40 shadow-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {DISEASES.map((d) => (
                        <SelectItem key={d.key} value={d.key}>
                          {d.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <span className="text-slate-400 font-medium">vs</span>
                  <Select value={disease2} onValueChange={setDisease2}>
                    <SelectTrigger className="w-40 shadow-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {DISEASES.map((d) => (
                        <SelectItem key={d.key} value={d.key}>
                          {d.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <Button
                  variant={chartMode === "overlay" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setChartMode("overlay")}
                  className="shadow-sm hover:shadow-md transition-all duration-200"
                >
                  Overlay
                </Button>
                <Button
                  variant={chartMode === "side" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setChartMode("side")}
                  className="shadow-sm hover:shadow-md transition-all duration-200"
                >
                  Side-by-Side
                </Button>
                <Button
                  variant={showForecast ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowForecast((v) => !v)}
                  className="shadow-sm hover:shadow-md transition-all duration-200"
                >
                  <Activity className="h-4 w-4 mr-2" />
                  Forecast
                </Button>
              </div>
            </div>

            <div className="flex flex-col lg:flex-row gap-4">
              <DiseaseInfoBox disease={disease1} />
              <DiseaseInfoBox disease={disease2} />
            </div>
          </CardContent>
        </Card>

        {/* Advanced Charts */}
        <div className={`grid gap-6 ${chartMode === "side" ? "grid-cols-1 xl:grid-cols-2" : "grid-cols-1"}`}>
          {/* Trend Analysis */}
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 text-white" />
                </div>
                <span className="text-slate-800">Disease Trend Analysis</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={350}>
                {chartMode === "overlay" ? (
                  <AreaChart data={forecastData}>
                    <defs>
                      <linearGradient id="d1Gradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={getDiseaseMeta(disease1).color} stopOpacity={0.8} />
                        <stop offset="95%" stopColor={getDiseaseMeta(disease1).color} stopOpacity={0.1} />
                      </linearGradient>
                      <linearGradient id="d2Gradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={getDiseaseMeta(disease2).color} stopOpacity={0.8} />
                        <stop offset="95%" stopColor={getDiseaseMeta(disease2).color} stopOpacity={0.1} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "white",
                        border: "1px solid #e2e8f0",
                        borderRadius: "12px",
                        boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                      }}
                      formatter={(value, name, props) => {
                        const idx =
                          props.payload && props.payload[0] && props.payload[0].payload
                            ? forecastData.findIndex((d) => d.month === props.payload[0].payload.month)
                            : -1
                        const percent = getPercentChange(forecastData, idx, props.dataKey)
                        return [value, `${name} ${percent ? `(${percent}% change)` : ""}`]
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="d1"
                      stroke={getDiseaseMeta(disease1).color}
                      fillOpacity={1}
                      fill="url(#d1Gradient)"
                      name={getDiseaseMeta(disease1).label}
                      strokeWidth={3}
                    />
                    <Area
                      type="monotone"
                      dataKey="d2"
                      stroke={getDiseaseMeta(disease2).color}
                      fillOpacity={1}
                      fill="url(#d2Gradient)"
                      name={getDiseaseMeta(disease2).label}
                      strokeWidth={3}
                    />
                    <ReferenceDot
                      x={annotationMonth}
                      y={forecastData.find((d) => d.month === annotationMonth)?.d1}
                      r={6}
                      fill="#f59e42"
                      stroke="white"
                      strokeWidth={2}
                      label={{ value: "Outbreak", position: "top" }}
                    />
                  </AreaChart>
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={forecastData}>
                        <defs>
                          <linearGradient id="d1Gradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={getDiseaseMeta(disease1).color} stopOpacity={0.8} />
                            <stop offset="95%" stopColor={getDiseaseMeta(disease1).color} stopOpacity={0.1} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                        <YAxis stroke="#64748b" fontSize={12} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "white",
                            border: "1px solid #e2e8f0",
                            borderRadius: "8px",
                            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="d1"
                          stroke={getDiseaseMeta(disease1).color}
                          fillOpacity={1}
                          fill="url(#d1Gradient)"
                          name={getDiseaseMeta(disease1).label}
                          strokeWidth={3}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={forecastData}>
                        <defs>
                          <linearGradient id="d2Gradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={getDiseaseMeta(disease2).color} stopOpacity={0.8} />
                            <stop offset="95%" stopColor={getDiseaseMeta(disease2).color} stopOpacity={0.1} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                        <YAxis stroke="#64748b" fontSize={12} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "white",
                            border: "1px solid #e2e8f0",
                            borderRadius: "8px",
                            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="d2"
                          stroke={getDiseaseMeta(disease2).color}
                          fillOpacity={1}
                          fill="url(#d2Gradient)"
                          name={getDiseaseMeta(disease2).label}
                          strokeWidth={3}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Correlation Analysis */}
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <BarChart3 className="h-4 w-4 text-white" />
                </div>
                <span className="text-slate-800">Disease Correlation by Region</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={350}>
                <ScatterChart
                  data={diabetesData.map((item, index) => ({
                    region: item.region,
                    diabetes: item.rate,
                    malaria: malariaData[index]?.rate || 0,
                    population: item.population / 1000000,
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis type="number" dataKey="diabetes" name="Diabetes Rate" stroke="#64748b" fontSize={12} />
                  <YAxis type="number" dataKey="malaria" name="Malaria Rate" stroke="#64748b" fontSize={12} />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    contentStyle={{
                      backgroundColor: "white",
                      border: "1px solid #e2e8f0",
                      borderRadius: "12px",
                      boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                    }}
                    formatter={(value, name) => [value.toFixed(2), name]}
                  />
                  <Scatter dataKey="population" fill="#22c55e" name="Population (M)" r={6} />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* AI Insights Placeholder */}
        <Card className="shadow-lg border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <RefreshCw className="h-4 w-4 text-white animate-spin" />
              </div>
              <span className="text-slate-800">AI Insights</span>
              <span className="text-sm bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">Coming Soon</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="bg-white/50 rounded-lg p-6 border border-blue-200">
              <p className="text-slate-600 leading-relaxed">
                This section will provide AI-powered predictions, anomaly detection, and natural language Q&A about your
                health data. Get intelligent insights and recommendations based on advanced machine learning algorithms.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Hotspots Table */}
        <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center space-x-3">
              <span className="text-slate-800">Hotspots in Weija Municipal</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm text-slate-700">
                <thead>
                  <tr className="bg-slate-100">
                    <th className="px-4 py-2 text-left">Locality</th>
                    <th className="px-4 py-2 text-left">Disease</th>
                    <th className="px-4 py-2 text-left">Cases</th>
                    <th className="px-4 py-2 text-left">Population</th>
                    <th className="px-4 py-2 text-left">Rate (per 1000)</th>
                  </tr>
                </thead>
                <tbody>
                  {HOTSPOTS.map((row, i) => (
                    <tr key={i} className="border-b">
                      <td className="px-4 py-2">{row.locality}</td>
                      <td className="px-4 py-2">{row.disease}</td>
                      <td className="px-4 py-2">{row.cases}</td>
                      <td className="px-4 py-2">{row.population}</td>
                      <td className="px-4 py-2">{((row.cases / row.population) * 1000).toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Demographic Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Cases by Age Group</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={AGE_DISTRIBUTION}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="age" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="cases" fill="#6366f1" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Cases by Sex</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={SEX_DISTRIBUTION} dataKey="cases" nameKey="sex" cx="50%" cy="50%" outerRadius={80} fill="#22c55e" label />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Diagnosis Patterns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Top Principal Diagnoses</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={PRINCIPAL_DIAGNOSES}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="diagnosis" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Top Additional Diagnoses</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={ADDITIONAL_DIAGNOSES}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="diagnosis" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#6366f1" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* NHIA & Pregnancy Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>NHIA Status</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={NHIA_STATUS} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={80} fill="#6366f1" label />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Pregnancy Status</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={PREGNANCY_STATUS} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={80} fill="#22c55e" label />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Trends by Locality */}
        <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
          <CardHeader className="pb-4">
            <CardTitle>Trends by Locality</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={TRENDS_BY_LOCALITY}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="MADINA-NEW RD" stroke="#22c55e" strokeWidth={2} />
                <Line type="monotone" dataKey="GBAWE, TELECOM" stroke="#6366f1" strokeWidth={2} />
                <Line type="monotone" dataKey="KWASHIEMAN" stroke="#ef4444" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Feedback Button */}
        <div className="fixed bottom-8 right-8 z-50">
          <Button
            size="lg"
            onClick={() => alert("Feedback form coming soon!")}
            className="shadow-xl hover:shadow-2xl transition-all duration-300 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-full px-6 py-3"
          >
            💬 Feedback
          </Button>
        </div>
      </div>
    </div>
  )
}

export default Analytics
