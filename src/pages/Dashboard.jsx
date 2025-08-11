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
import api from "../api"
import { useEffect, useState } from "react"
import { useDiseaseYears } from "../data/all_years";
import { useDiseases } from "../data/all_diseases";
import { useDashboardData, useDashboardDataRegionRates } from "../data/dashboard_data";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select"
import { GenderDistribution } from "../components/PieChartData";
import { DiabetesDataStats } from "../components/dashboard/DiseaseData/DiabetesDataStats";
import { MeningitisDataStats } from "../components/dashboard/DiseaseData/MeningitisDataStats";
import { CholeraDataStats } from "../components/dashboard/DiseaseData/CholeraDataStats";
import { MalariaDataStats } from "../components/dashboard/DiseaseData/MalariaDataStats";
import { DiabetesDiseaseRates } from "../components/dashboard/DiseaseRates/DiabetesDiseaseRates";
import { MeningitisDiseaseRates } from "../components/dashboard/DiseaseRates/MeningitisDiseaseRates";
import { CholeraDiseaseRates } from "../components/dashboard/DiseaseRates/CholeraDiseaseRates";
import { MalariaDiseaseRates } from "../components/dashboard/DiseaseRates/MalariaDiseaseRates";

const Dashboard = () => {
  const { data: diseases, isLoading: isDiseasesLoading, error } = useDiseases();
  const [selectedDisease, setSelectedDisease] = useState(() => {
    return localStorage.getItem("selectedDisease") || "Diabetes";
  });
  const [isLiveDataEnabled, setIsLiveDataEnabled] = useState(() => {
    return localStorage.getItem("isLiveDataEnabled") === "true" || false;
  });

  const handleDiseaseChange = (value) => {
    setSelectedDisease(value);
    localStorage.setItem("selectedDisease", value);
  };

  const handleDiseaseYearChange = (value) => {
    setSelectedDiseaseYear(value);
    localStorage.setItem("selectedDiseaseYear", value);
  };

  const handleLiveDataToggle = () => {
    const newValue = !isLiveDataEnabled;
    setIsLiveDataEnabled(newValue);
    localStorage.setItem("isLiveDataEnabled", newValue.toString());
  };

  const selectedDiseaseId = diseases?.find(
    (disease) => disease.disease_name === selectedDisease
  )?.id;

  const {
    data: diseaseYears,
    isLoading: isDiseaseYearsLoading,
    error: isDiseaseYearsError,
  } = useDiseaseYears(selectedDiseaseId);


  const selectedDiseaseL = selectedDisease.toLowerCase();
  const [selectedDiseaseYear, setSelectedDiseaseYear] = useState(() => {
    return (
      localStorage.getItem("selectedDiseaseYear") ||
      String(new Date().getFullYear())
    );
  });



  // const [dashboardData, setDashboardData] = useState(null);
  // const [loading, setLoading] = useState(true);
  // const [error, setError] = useState(null);

  // const getDashBoardData = async () => {
  //   try {
  //     setLoading(true)
  //     const response = await api.get('disease/dashboard/?year=2025');
  //     setDashboardData(response.data)
  //   } catch (error) {
  //     setError(error.message)
  //   } finally {

  // }setLoading(false);
  //   }

  // useEffect(() => {
  //   getDashBoardData();
  // }, [])

  const COLORS = ["#22c55e", "#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6"]

  const diseaseDistribution = [
    { name: "Malaria", value: healthMetrics.totalMalariaCases, color: "#ef4444" },
    { name: "Diabetes", value: healthMetrics.totalDiabetesCases, color: "#22c55e" },
  ]

  const {
    data: dashboardData,
    isLoading: isDashboardDataLoading,
    error: isDashboardDataError,
  } = useDashboardData(selectedDisease, selectedDiseaseYear);

  

  const {
    data: dashboardDataRegionRates,
    isLoading: isDashboardDataRegionRatesLoading,
    error: isDashboardDataRegionRatesError,
  } = useDashboardDataRegionRates(selectedDiseaseL, selectedDiseaseYear);

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
        return null;
    }
  }

  const diseaseRates = (selectedDisease) => {
    switch (selectedDisease) {
      case "Diabetes":
        return DiabetesDiseaseRates({ dashboardDataRegionRates, isDashboardDataRegionRatesLoading, isDashboardDataRegionRatesError, selectedDisease, selectedDiseaseYear });
      case "Meningitis":
        return MeningitisDiseaseRates({ dashboardDataRegionRates, isDashboardDataRegionRatesLoading, isDashboardDataRegionRatesError, selectedDisease, selectedDiseaseYear });
      case "Cholera":
        return CholeraDiseaseRates({ dashboardDataRegionRates, isDashboardDataRegionRatesLoading, isDashboardDataRegionRatesError, selectedDisease, selectedDiseaseYear });
      case "Malaria":
        return MalariaDiseaseRates({ dashboardDataRegionRates, isDashboardDataRegionRatesLoading, isDashboardDataRegionRatesError, selectedDisease, selectedDiseaseYear });
      default:
        return null;
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Health Dashboard</h1>
          <p className="text-gray-500">Ghana Disease Monitoring & Analytics</p>
        </div>

        <div className="flex items-center space-x-4">
          {/* Live Data Toggle */}
          <div className="flex flex-col items-center mr-4">
            <span className="mb-1 text-xs font-semibold text-gray-600">Live Data</span>
            <button
              onClick={handleLiveDataToggle}
              type="button"
              className={`relative w-16 h-7 rounded-full transition-colors duration-300 focus:outline-none border-2 flex items-center px-1 ${
                isLiveDataEnabled
                  ? 'bg-green-400 border-green-300'
                  : 'bg-red-400 border-red-300'
              }`}
              aria-pressed={isLiveDataEnabled}
            >
              {/* ON label */}
              <span className={`absolute left-2 text-xs font-bold transition-opacity duration-200 ${isLiveDataEnabled ? 'opacity-100 text-white' : 'opacity-0'}`}>ON</span>
              {/* OFF label */}
              <span className={`absolute right-2 text-xs font-bold transition-opacity duration-200 ${!isLiveDataEnabled ? 'opacity-100 text-white' : 'opacity-0'}`}>OFF</span>
              {/* Switch knob */}
              <span
                className={`inline-block w-5 h-5 bg-white rounded-full shadow-md transform transition-transform duration-300 ${
                  isLiveDataEnabled ? 'translate-x-8' : 'translate-x-0'
                }`}
              ></span>
            </button>
          </div>

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

      {/* Key Metrics */}
      {/* <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"> */}
      {/* {loading ? (
          <div>Loading...</div>
        ) : error ? (
          <div>Error: {typeof error === 'string' ? error : error?.message || 'An error occurred'}</div>
        ) : dashboardData?.diabetes ? (

          <MetricCard
            title={dashboardData.diabetes.title}
            value={dashboardData.diabetes.total_count.toLocaleString()}
            change={healthMetrics.monthlyGrowthDiabetes}
            icon={Heart}
            trend="up"
            color="health"
          />
        ) : (
          <div>No data available</div>
        )} */}
      {/* <MetricCard
          title="Total Malaria Cases"
          value={healthMetrics.totalMalariaCases.toLocaleString()}
          change={Math.abs(healthMetrics.monthlyGrowthMalaria)}
          icon={Droplets}
          trend="down"
          color="danger"
        /> */}
      {/* <MetricCard title="Critical Hotspots" value={healthMetrics.criticalHotspots} icon={MapPin} color="warning" /> */}
      {/* <MetricCard
          title="Population at Risk"
          value={`${(healthMetrics.populationAtRisk / 1000000).toFixed(1)}M`}
          icon={Users}
          color="info"
        /> */}
      {/* </div> */}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Trends */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300 col-span-1">
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
        {/* <Card className="col-span-1">
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
        </Card> */}

        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
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

      </div>

      {/* Regional Comparison */}
      <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
        <div className="space-y-4">
          {/* Regional Comparison Header with Controls */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Regional Disease Rates</h2>
              <p className="text-gray-500">Compare disease rates across different regions</p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Disease Selection for Regional Chart */}
              <Select value={selectedDisease} onValueChange={handleDiseaseChange}>
                <SelectTrigger className="w-[180px]">
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
              
              {/* Year Selection for Regional Chart */}
              <Select
                value={selectedDiseaseYear}
                onValueChange={handleDiseaseYearChange}
              >
                <SelectTrigger className="w-[150px]">
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
            </div>
          </div>
          
          {/* Regional Chart */}
          {selectedDisease && diseaseRates(selectedDisease)}
        </div>
      </Card>
      {/* <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart className="h-5 w-5 text-health-400" />
            <span>Regional Disease Rates (per 1000 population) - {selectedDisease} - {selectedDiseaseYear}</span>
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
      </Card> */}
    </div>
  )
}

export default Dashboard
