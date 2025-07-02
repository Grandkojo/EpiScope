import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { LineChart } from "../components/charts/LineChart";
import { StatCard } from "../components/dashboard/StatCard";
import {
  healthMetrics,
  monthlyTrends,
  ghanaRegions,
  hotspots,
  diseases_,
  years,
} from "../data/dummyData";
import {
  Activity,
  HeartPulse,
  TrendingUp,
  TrendingDown,
  TestTubeDiagonal,
  Users,
  MapPin,
  AlertTriangle,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { useDiseaseYears } from "../data/all_years";
import { useDiseases } from "../data/all_dseases";
import { useDashboardData } from "../data/dashboard_data";
import { useState, useEffect } from "react";
import { Loader2, AlertCircle } from "lucide-react";
import api from "../api";
import { useQuery } from "@tanstack/react-query";
import { data } from "react-router-dom";
import { Skull } from "lucide-react";
import { useQueuedNotifications } from "../hooks/use-queued-notifications";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  ResponsiveContainer,
  Line,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { GenderDistribution } from "../components/PieChartData";
import { DiabetesDataStats } from "../components/dashboard/DiseaseData/DiabetesDataStats";
import { MeningitisDataStats } from "../components/dashboard/DiseaseData/MeningitisDataStats";
import { CholeraDataStats } from "../components/dashboard/DiseaseData/CholeraDataStats";
const UserDashboard = () => {

  useQueuedNotifications();

  const [selectedHotspot, setSelectedHotspot] = useState(null);
  const [filterSeverity, setFilterSeverity] = useState("all");

  const filteredHotspots = hotspots.filter(
    (hotspot) =>
      filterSeverity === "all" || hotspot.severity === filterSeverity
  );

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "high":
        return "bg-red-500/20 text-red-500 border-red-500/30";
      case "medium":
        return "bg-yellow-400/20 text-yellow-500 border-yellow-400/30";
      case "low":
        return "bg-green-400/20 text-green-500 border-green-400/30";
      default:
        return "bg-gray-500/20 text-gray-500 border-gray-500/30";
    }
  };

  useEffect(() => {
    console.log("Dashboard Content mounted");
    const stored = sessionStorage.getItem("queuedNotifications");
    console.log("SessionStorage on Dashboard:", stored);
  }, []);
  // const [dashboardData, setDashboardData] = useState(null);

  // const [loading, setLoading] = useState(true);
  // const [error, setError] = useState(null);

  // const getDashBoardData = async () => {
  //   try {
  //     setLoading(true);
  //     const response = await api.get("diseases/dashboard/?year=2025");
  //     setDashboardData(response.data);
  //   } catch (error) {
  //     setError(error.message);
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  // useEffect(() => {
  //   getDashBoardData();
  // }, []);

  const [dashboard, setDashboard] = useState("");
  const [selectedRegion, setSelectedRegion] = useState("Greater Accra");

  const [selectedDisease, setSelectedDisease] = useState(() => {
    return localStorage.getItem("selectedDisease") || "Diabetes";
  });
  const selectedDiseaseL = selectedDisease.toLowerCase();
  const [selectedDiseaseYear, setSelectedDiseaseYear] = useState(() => {
    return (
      localStorage.getItem("selectedDiseaseYear") ||
      String(new Date().getFullYear())
    );
  });
  const { data: diseases, isLoading: isDiseasesLoading, error } = useDiseases();

  const selectedDiseaseId = diseases?.find(
    (disease) => disease.disease_name === selectedDisease
  )?.id;

  const {
    data: diseaseYears,
    isLoading: isDiseaseYearsLoading,
    error: isDiseaseYearsError,
  } = useDiseaseYears(selectedDiseaseId);

  const {
    data: dashboardData,
    isLoading: isDashboardDataLoading,
    error: isDashboardDataError,
  } = useDashboardData(selectedDisease, selectedDiseaseYear);
  // const {data: diseaseYears, isLoading, error} = useDiseaseYears()
  // Transform monthly trends data for the selected region
  const regionTrends = monthlyTrends.map((trend) => ({
    month: trend.month,
    diabetes: Math.round(
      trend.diabetes * (selectedRegion === "All Regions" ? 1 : 0.15)
    ),
    malaria: Math.round(
      trend.malaria * (selectedRegion === "All Regions" ? 1 : 0.15)
    ),
  }));

  // Disease distribution data
  // const diseaseDistribution = [
  //   { name: "Diabetes", value: 35 },
  //   { name: "Malaria", value: 45 },
  //   { name: "Other", value: 20 },
  // ];

  // <Card className="col-span-1">
  //   <CardHeader>
  //     <CardTitle className="flex items-center space-x-2">
  //       <AlertTriangle className="h-5 w-5 text-health-400" />
  //       <span>Disease Distribution</span>
  //     </CardTitle>
  //   </CardHeader>
  //   <CardContent>
  //     <ResponsiveContainer width="100%" height={300}>
  //       <PieChart>
  //         <Pie
  //           data={diseaseDistribution}
  //           cx="50%"
  //           cy="50%"
  //           outerRadius={100}
  //           fill="#8884d8"
  //           dataKey="value"
  //           label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
  //         >
  //           {diseaseDistribution.map((entry, index) => (
  //             <Cell key={`cell-${index}`} fill={entry.color} />
  //           ))}
  //         </Pie>
  //         <Tooltip
  //           contentStyle={{
  //             backgroundColor: "#1f2937",
  //             border: "1px solid #374151",
  //             borderRadius: "8px",
  //           }}
  //         />
  //       </PieChart>
  //     </ResponsiveContainer>
  //   </CardContent>
  // </Card>

  // Get hotspots for selected region
  const regionHotspots =
    selectedRegion === "All Regions"
      ? hotspots
      : hotspots.filter((hotspot) => hotspot.region === selectedRegion);

  const handleDiseaseChange = (value) => {
    setSelectedDisease(value);
    localStorage.setItem("selectedDisease", value);
  };

  const handleDiseaseYearChange = (value) => {
    setSelectedDiseaseYear(value);
    localStorage.setItem("selectedDiseaseYear", value);
  };

  const diseaseStats = (selectedDisease) => {
    switch (selectedDisease) {
      case "Diabetes":
        return DiabetesDataStats(dashboardData, isDashboardDataLoading, error, selectedDiseaseL);
      case "Meningitis":
        return MeningitisDataStats(dashboardData, isDashboardDataLoading, error, selectedDiseaseL);
      case "Cholera":
        return CholeraDataStats(dashboardData, isDashboardDataLoading, error, selectedDiseaseL);
      case "Malaria":
        return MalariaDataStats(dashboardData, isDashboardDataLoading, error, selectedDiseaseL);
      default:
        return {};
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">
          My Health Dashboard
        </h1>
        <div className="flex">
          {/* Diseases available */}
          <Select value={selectedDisease} onValueChange={handleDiseaseChange}>
            <SelectTrigger className="w-[180px] mr-5">
              <SelectValue placeholder="Select Disease" />
            </SelectTrigger>
            <SelectContent>
              {isDiseasesLoading ? (
                <SelectItem value="loading" disabled>
                  Loading diseases...
                </SelectItem>
              ) : (
                <>
                  {diseases?.find(
                    (disease) => disease.disease_name === "Diabetes"
                  ) && <SelectItem value="Diabetes">Diabetes</SelectItem>}
                  {Array.isArray(diseases) &&
                    diseases
                      .filter((disease) => disease.disease_name !== "Diabetes")
                      .map((disease) => (
                        <SelectItem
                          key={disease.id}
                          value={disease.disease_name}
                        >
                          {disease.disease_name}
                        </SelectItem>
                      ))}
                </>
              )}
            </SelectContent>
          </Select>
          {/* Years available per year*/}
          <Select
            value={selectedDiseaseYear}
            onValueChange={handleDiseaseYearChange}
          >
            <SelectTrigger className="w-[150px] mr-5">
              <SelectValue placeholder="Select Year" />
            </SelectTrigger>
            <SelectContent>
              {isDiseaseYearsLoading ? (
                <SelectItem value="loading" disabled>
                  Loading years...
                </SelectItem>
              ) : (
                <>
                  <SelectItem value="all">All Years</SelectItem>
                  {diseaseYears?.find(
                    (disease) => disease.periodname === 2025
                  ) && <SelectItem value="2025">2025</SelectItem>}
                  {Array.isArray(diseaseYears) &&
                    diseaseYears
                      .filter((diseaseYear) => diseaseYear.periodname !== 2025)
                      .map((diseaseYear) => (
                        <SelectItem
                          key={diseaseYear.id}
                          value={diseaseYear.periodname}
                        >
                          {diseaseYear.periodname}
                        </SelectItem>
                      ))}
                </>
              )}
            </SelectContent>
          </Select>

          {/* <Select value={selectedRegion} onValueChange={setSelectedRegion}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select Region" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All Regions">All Regions</SelectItem>
              {ghanaRegions.map((region) => (
                <SelectItem key={region} value={region}>
                  {region}
                </SelectItem>
              ))}
            </SelectContent>
          </Select> */}
        </div>
      </div>

      {/* Stats Overview */}
      {
        selectedDisease && diseaseStats(selectedDisease)
      }
      

      <div className="grid gap-6 md:grid-cols-2">
        {/* Health Trends */}
        {/* <Card>
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
        </Card> */}

        {/* Disease Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Disease Distribution (Gender)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                {isDashboardDataLoading ? (
                   <text x="50%" y="50%" textAnchor="middle" dy=".3em" fill="#666">
                    Loading...
                 </text>
                ) : dashboardData?.[selectedDiseaseL]?.male_count && dashboardData?.[selectedDiseaseL]?.female_count ? (
                  <Pie
                    data={GenderDistribution(dashboardData?.[selectedDiseaseL]?.male_count, dashboardData?.[selectedDiseaseL]?.female_count)}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                  >
                    {GenderDistribution(dashboardData?.[selectedDiseaseL]?.male_count, dashboardData?.[selectedDiseaseL]?.female_count).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                ) : (
                  <text x="50%" y="50%" textAnchor="middle" dy=".3em" fill="#666">
                    No data available
                  </text>
                )}
                <Tooltip
                  contentStyle={{
                    backgroundColor: "grey",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* AI Insights */}
        <Card>
          <CardHeader>
            <CardTitle>AI Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <p>
                This is just a placeholder for the AI insights.
              </p>
            </ResponsiveContainer>

          </CardContent>
        </Card>
      </div>

      {/* Hotspots */}
      <Card>
        <CardHeader>
          <CardTitle>Health Hotspots in {selectedRegion}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative h-96 bg-gradient-to-br from-slate-900/20 to-green-800/10 rounded-xl border border-border overflow-hidden shadow-inner">
            <div className="absolute inset-0 bg-[url('/ghana-map.svg')] bg-center bg-contain bg-no-repeat opacity-10"></div>


            {/* Markers */}
            {filteredHotspots.map((hotspot) => (
              <div
                key={hotspot.id}
                className={`absolute w-4 h-4 rounded-full cursor-pointer transition-all duration-200 hover:scale-150 z-10 ${hotspot.severity === "high"
                    ? "bg-red-500"
                    : hotspot.severity === "medium"
                      ? "bg-yellow-400"
                      : "bg-green-500"
                  }`}
                style={{
                  left: `${(hotspot.lng + 3) * 15 + 20}%`,
                  top: `${(11 - hotspot.lat) * 8 + 10}%`,
                }}
                onClick={() => setSelectedHotspot(hotspot)}
              >
                <span className="absolute inset-0 rounded-full group-hover:animate-ping opacity-50 blur-sm"></span>
              </div>
            ))}

            <div className="absolute top-4 left-4 text-sm text-muted-foreground">
              <p className="font-medium">Hotspot Overview</p>
              <p className="text-xs">Click markers to view more</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hotspot Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredHotspots.map((hotspot) => (
          <Card
            key={hotspot.id}
            onClick={() => setSelectedHotspot(hotspot)}
            className={`transition-transform duration-300 cursor-pointer hover:scale-[1.02] hover:shadow-xl ${selectedHotspot?.id === hotspot.id
                ? "ring-2 ring-purple-500/60"
                : ""
              }`}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold">
                  {hotspot.region}
                </CardTitle>
                <div
                  className={`px-2 py-1 rounded-full text-xs font-semibold uppercase border shadow-sm ${getSeverityColor(
                    hotspot.severity
                  )}`}
                >
                  {hotspot.severity}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-red-500" />
                  <div>
                    <p className="text-muted-foreground text-xs">
                      Malaria Rate
                    </p>
                    <p className="font-bold">
                      {hotspot.malariaRate.toFixed(1)}%
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-green-500" />
                  <div>
                    <p className="text-muted-foreground text-xs">
                      Diabetes Rate
                    </p>
                    <p className="font-bold">
                      {hotspot.diabetesRate.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-blue-500" />
                <div>
                  <p className="text-muted-foreground text-xs">Population</p>
                  <p className="font-bold">
                    {hotspot.population.toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="pt-2 border-t border-border">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Risk Level</span>
                  <span className="flex items-center gap-1">
                    <AlertTriangle className="h-3 w-3 text-yellow-500" />
                    {hotspot.severity}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Selected Hotspot Details */}
      {selectedHotspot && (
        <Card className="border border-purple-500/20 shadow-md rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg text-purple-600">
              <MapPin className="h-5 w-5" />
              <span>{selectedHotspot.region} – Detailed Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-muted-foreground">
              <div className="space-y-2">
                <h3 className="font-semibold text-foreground">Geography</h3>
                <p>
                  <strong className="text-foreground">Lat:</strong>{" "}
                  {selectedHotspot.lat}
                </p>
                <p>
                  <strong className="text-foreground">Lng:</strong>{" "}
                  {selectedHotspot.lng}
                </p>
                <p>
                  <strong className="text-foreground">Population:</strong>{" "}
                  {selectedHotspot.population.toLocaleString()}
                </p>
              </div>

              <div className="space-y-2">
                <h3 className="font-semibold text-foreground">Disease Rates</h3>
                <p>
                  <strong className="text-foreground">Malaria:</strong>{" "}
                  {selectedHotspot.malariaRate.toFixed(2)}%
                </p>
                <p>
                  <strong className="text-foreground">Diabetes:</strong>{" "}
                  {selectedHotspot.diabetesRate.toFixed(2)}%
                </p>
                <p>
                  <strong className="text-foreground">Risk Level:</strong>{" "}
                  {selectedHotspot.severity}
                </p>
              </div>

              <div className="space-y-2">
                <h3 className="font-semibold text-foreground">
                  Recommendations
                </h3>
                <ul className="list-disc list-inside text-xs space-y-1">
                  <li>Increase healthcare facilities</li>
                  <li>Community awareness programs</li>
                  <li>Disease monitoring tech</li>
                  <li>Policy intervention & support</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      

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
  );
};

export default UserDashboard;
