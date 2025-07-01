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

const UserDashboard = () => {
  
  useQueuedNotifications();

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
  const diseaseDistribution = [
    { name: "Malaria", value: healthMetrics.totalMalariaCases, color: "#ef4444" },
    { name: "Diabetes", value: healthMetrics.totalDiabetesCases, color: "#22c55e" },
  ]
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
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Display counts */}
        <StatCard
          title={
            dashboardData?.error
              ? "Error"
              : dashboardData?.[selectedDiseaseL]
              ? `${dashboardData?.[selectedDiseaseL]?.title} - ${dashboardData?.[selectedDiseaseL]?.year}`
              : "Loading..."
          }
          value={
            isDashboardDataLoading
              ? "..."
              : dashboardData?.error
              ? "No data"
              : dashboardData?.[selectedDiseaseL]?.total_count || 0
          }
          description={
            isDashboardDataLoading ? (
              "Loading data..."
            ) : dashboardData?.error ? (
              dashboardData.error
            ) : dashboardData?.[selectedDiseaseL]?.delta_vals === "up" ? (
              <TrendingUp className="h-4 w-4 text-orange-500" />
            ) : (
              "No delta rate"
            )
          }
          icon={
            isDashboardDataLoading ? (
              <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
            ) : dashboardData?.error ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : (
              <TrendingUp className="h-4 w-4 text-orange-500" />
            )
          }
          isLoading={isDashboardDataLoading}
          error={dashboardData?.error || error}
        />

        {/* {<StatCard
          title="Death Counts"
          value={Math.round(
            healthMetrics.populationAtRisk *
            (selectedRegion === "All Regions" ? 1 : 0.15)
          )}
          description="In your region"
          // icon={<Users className="h-4 w-4 text-purple-500" />}
          icon={<Skull className="h-5 w-5 text-red-600" />}

        />} */}

        <StatCard
          title={
            dashboardData?.error
              ? "Error"
              : dashboardData?.[selectedDiseaseL]
              ? "Death Counts"
              : "Loading..."
          }
          value={
            isDashboardDataLoading
              ? "..."
              : dashboardData?.error
              ? "No data"
              : dashboardData?.[selectedDiseaseL]?.deaths_count || 0
          }
          description={
            isDashboardDataLoading ? (
              "Loading data..."
            ) : dashboardData?.error ? (
              dashboardData.error
            ) : dashboardData?.[selectedDiseaseL]?.delta_vals === "up" ? (
              <Skull className="h-5 w-5 text-red-600" />
            ) : (
              "No delta rate"
            )
          }
          icon={
            isDashboardDataLoading ? (
              <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
            ) : dashboardData?.error ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : (
              <Skull className="h-5 w-5 text-red-600" />
            )
          }
          isLoading={isDashboardDataLoading}
          error={dashboardData?.error || error}
        />

        <StatCard
          title={
            dashboardData?.error
              ? "Error"
              : dashboardData?.[selectedDiseaseL]
              ? "Lab Confirmed Cases"
              : "Loading..."
          }
          value={
            isDashboardDataLoading
              ? "..."
              : dashboardData?.error
              ? "No data"
              : dashboardData?.[selectedDiseaseL]?.lab_confirmed_cases_count ||
                0
          }
          description={
            isDashboardDataLoading ? (
              "Loading data..."
            ) : dashboardData?.error ? (
              dashboardData.error
            ) : dashboardData?.[selectedDiseaseL]?.delta_vals === "up" ? (
              <TestTubeDiagonal className="h-5 w-5 text-red-600" />
            ) : (
              "No delta rate"
            )
          }
          icon={
            isDashboardDataLoading ? (
              <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
            ) : dashboardData?.error ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : (
              <TestTubeDiagonal className="h-5 w-5 text-red-600" />
            )
          }
          isLoading={isDashboardDataLoading}
          error={dashboardData?.error || error}
        />

        <StatCard
          title="Health Status"
          value="Good"
          description="Your current health status"
          icon={<HeartPulse className="h-4 w-4 text-green-500" />}
        />

        {/* <StatCard
          title="Risk Level"
          value="Low"
          description="Based on your region"
          icon={<Activity className="h-4 w-4 text-blue-500" />}
        /> */}

        {/* 

        <StatCard
          title="Death Counts"
          value={Math.round(
            healthMetrics.populationAtRisk *
              (selectedRegion === "All Regions" ? 1 : 0.15)
          )}
          description="In your region"
          // icon={<Users className="h-4 w-4 text-purple-500" />}
          icon={<Skull className="h-5 w-5 text-red-600" />}

        /> */}
      </div>

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
            <CardTitle>Disease Distribution</CardTitle>
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
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {diseaseDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
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
                  <AlertTriangle
                    className={`h-5 w-5 ${
                      hotspot.severity === "high"
                        ? "text-red-500"
                        : hotspot.severity === "medium"
                        ? "text-yellow-500"
                        : "text-green-500"
                    }`}
                  />
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

      {/* Hotspots Section Styled Like Hotspots.jsx */}
      {/* {<Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-foreground">
            Health Hotspots in {selectedRegion}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {regionHotspots.map((hotspot) => (
              <Card
                key={hotspot.id}
                className="transition-transform duration-300 hover:scale-[1.02] hover:shadow-lg"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-medium">
                      {hotspot.region}
                    </CardTitle>
                    <div
                      className={`px-2 py-1 rounded-full text-xs font-semibold uppercase border ${hotspot.severity === "high"
                        ? "bg-red-500/20 text-red-500 border-red-500/30"
                        : hotspot.severity === "medium"
                          ? "bg-yellow-400/20 text-yellow-500 border-yellow-400/30"
                          : "bg-green-400/20 text-green-500 border-green-400/30"
                        }`}
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
                        <p className="text-xs text-muted-foreground">Malaria Rate</p>
                        <p className="font-semibold">
                          {hotspot.malariaRate.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Activity className="h-4 w-4 text-green-500" />
                      <div>
                        <p className="text-xs text-muted-foreground">
                          Diabetes Rate
                        </p>
                        <p className="font-semibold">
                          {hotspot.diabetesRate.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-blue-500" />
                    <div>
                      <p className="text-xs text-muted-foreground">Population</p>
                      <p className="font-semibold">
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
        </CardContent>
      </Card>} */}

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
