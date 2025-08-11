import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "../components/ui/select"
import SearchableSelect from "../components/ui/SearchableSelect"
import DateRangePicker from "../components/ui/DateRangePicker"
import api from "../api"
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
  Cell,
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
  Brain,
  Target,
  MapPin,
  Clock,
  Shield,
  Lightbulb,
  TrendingDown,
  Eye,
  Heart,
  Activity as ActivityIcon,
  Search,
} from "lucide-react"
import { 
  useNHIAStatusAnalyticsData, 
  usePregnancyStatusAnalyticsData, 
  usePrincipalDiagnosesAnalyticsData, 
  useAdditionalDiagnosesAnalyticsData, 
  useSexDistributionAnalyticsData, 
  useAgeDistributionAnalyticsData,
  useLocalitiesTrendAnalyticsData
} from "../data/analytics_data"
import { useDiseaseYears } from "../data/all_years"
import { useDiseases } from "../data/all_diseases"
import { useLocalities } from "../data/all_localities"
import { useHospitals } from "../data/all_hospitals"
import { NHIAStatusDistribution, PregnancyStatusDistribution } from "../components/PieChartData"
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
const TRENDS_BY_LOCALITY = [
  { month: "Jan", "MADINA-NEW RD": 10, "GBAWE, TELECOM": 8, "KWASHIEMAN": 20 },
  { month: "Feb", "MADINA-NEW RD": 12, "GBAWE, TELECOM": 9, "KWASHIEMAN": 22 },
  { month: "Mar", "MADINA-NEW RD": 15, "GBAWE, TELECOM": 10, "KWASHIEMAN": 25 },
  { month: "Apr", "MADINA-NEW RD": 13, "GBAWE, TELECOM": 11, "KWASHIEMAN": 23 },
]

const Analytics = () => {

  const { data: hospitals, isLoading: isHospitalsLoading, error: isHospitalsError } = useHospitals();
  const { data: diseases, isLoading: isDiseasesLoading, error } = useDiseases();
  const [selectedDisease, setSelectedDisease] = useState(() => {
    return localStorage.getItem("selectedDisease") || "Diabetes";
  });
  const [selectedLocality, setSelectedLocality] = useState(() => {
    return localStorage.getItem("selectedLocality") || "all";
  });
  const [isLiveDataEnabled, setIsLiveDataEnabled] = useState(() => {
    return localStorage.getItem("isLiveDataEnabled") === "true" || false;
  });

  const [selectedHospital, setSelectedHospital] = useState(() => {
    return localStorage.getItem("selectedHospital") || "weija";
  });

  const handleHospitalChange = (value) => {
    setSelectedHospital(value);
    localStorage.setItem("selectedHospital", value);
  };

  const handleDiseaseChange = (value) => {
    setSelectedDisease(value);
    localStorage.setItem("selectedDisease", value);
  };

  const handleDiseaseYearChange = (value) => {
    setSelectedDiseaseYear(value);
    localStorage.setItem("selectedDiseaseYear", value);
  };

  const handleLocalityChange = (value) => {
    setSelectedLocality(value);
    localStorage.setItem("selectedLocality", value);
  };

  const selectedDiseaseId = diseases?.find(
    (disease) => disease.disease_name === selectedDisease
  )?.id;
  const {
    data: diseaseYears,
    isLoading: isDiseaseYearsLoading,
    error: isDiseaseYearsError,
  } = useDiseaseYears(selectedDiseaseId);

  const {
    data: localities,
    isLoading: isLocalitiesLoading,
    error: isLocalitiesError,
  } = useLocalities(selectedHospital);

  const selectedDiseaseL = selectedDisease.toLowerCase();
  const [selectedDiseaseYear, setSelectedDiseaseYear] = useState(() => {
    return (
      localStorage.getItem("selectedDiseaseYear") ||
      String(new Date().getFullYear())
    );
  });

  const {
    data: sexDistributionData,
    isLoading: isSexDistributionDataLoading,
    error: isSexDistributionDataError,
  } = useSexDistributionAnalyticsData(selectedDiseaseL, selectedDiseaseYear, selectedHospital);

  const {
    data: ageDistributionData,
    isLoading: isAgeDistributionDataLoading,
    error: isAgeDistributionDataError,
  } = useAgeDistributionAnalyticsData(selectedDiseaseL, selectedDiseaseYear, selectedHospital);

  const {
    data: principalDiagnosesData,
    isLoading: isPrincipalDiagnosesDataLoading,
    error: isPrincipalDiagnosesDataError,
  } = usePrincipalDiagnosesAnalyticsData(selectedDiseaseL, selectedDiseaseYear, selectedHospital);

  const {
    data: additionalDiagnosesData,
    isLoading: isAdditionalDiagnosesDataLoading,
    error: isAdditionalDiagnosesDataError,
  } = useAdditionalDiagnosesAnalyticsData(selectedDiseaseL, selectedDiseaseYear, selectedHospital);

  const {
    data: nhiaStatusData,
    isLoading: isNHIAStatusDataLoading,
    error: isNHIAStatusDataError,
  } = useNHIAStatusAnalyticsData(selectedDiseaseL, selectedDiseaseYear);
  const {
    data: pregnancyStatusData,
    isLoading: isPregnancyStatusDataLoading,
    error: isPregnancyStatusDataError,
  } = usePregnancyStatusAnalyticsData(selectedDiseaseL, selectedDiseaseYear);

  const {
    data: localitiesTrendData,
    isLoading: isLocalitiesTrendDataLoading,
    error: isLocalitiesTrendDataError,
  } = useLocalitiesTrendAnalyticsData(selectedDiseaseL, selectedDiseaseYear, selectedHospital, selectedLocality);

  // Disease dropdowns
  const [disease1, setDisease1] = useState("diabetes")
  const [disease2, setDisease2] = useState("malaria")

  // Chart mode
  const [chartMode, setChartMode] = useState("overlay") // or "side"

  // Date range (dummy)
  const [dateRange, setDateRange] = useState({ from: "2023-01", to: "2024-12" })
  const [customDateRange, setCustomDateRange] = useState(null)
  const [selectedDateRangeObj, setSelectedDateRangeObj] = useState(null)

  // Extract available years from disease years data
  const availableYears = diseaseYears 
    ? diseaseYears.map(year => year.periodname).filter(Boolean)
    : [];

  // Add fallback years if no data is available
  const finalAvailableYears = availableYears.length > 0 
    ? availableYears 
    : [2020, 2021, 2022, 2023, 2024, 2025]; // Fallback years

  // Handle custom date range change
  const handleCustomDateRangeChange = (apiFormat, dateRangeObj) => {
    setCustomDateRange(apiFormat);
    setSelectedDateRangeObj(dateRangeObj);
    console.log("Date range selected:", { apiFormat, dateRangeObj });
    
    // Optionally auto-trigger analytics when date range changes
    // Uncomment the line below if you want automatic analytics generation
    // handleFetchAnalytics();
  };

  // Structured Analytics State
  const [structuredAnalytics, setStructuredAnalytics] = useState(null);
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(false);
  const [analyticsError, setAnalyticsError] = useState(null);

  // Function to fetch structured analytics
  // This function uses the selected date range from the DateRangePicker
  // If no custom date range is selected, it falls back to a default range
  const fetchStructuredAnalytics = async () => {
    setIsLoadingAnalytics(true);
    setAnalyticsError(null);
    
    try {
      // Use the actual selected date range if available, otherwise fallback to default
      let dateRangeToUse = customDateRange;
      
      if (!dateRangeToUse) {
        // If no custom date range is selected, use the selected year with default months
        dateRangeToUse = `${selectedDiseaseYear}-03:${selectedDiseaseYear}-09`;
      }
      
      const requestBody = {
        hospital: selectedHospital,
        year: selectedDiseaseYear,
        date_range: dateRangeToUse,
        disease: selectedDiseaseL,
        locality: selectedLocality
      };

      console.log("Fetching structured analytics with:", requestBody);
      console.log("Selected date range object:", selectedDateRangeObj);
      
      const response = await api.post('ai/structured-analytics/', requestBody);
      
      if (response.data && response.data.data) {
        setStructuredAnalytics(response.data.data);
        console.log("Structured analytics received:", response.data.data);
      } else {
        throw new Error("Invalid response format");
      }
    } catch (error) {
      console.error("Error fetching structured analytics:", error);
      
      // Handle different types of errors
      let errorMessage = "Failed to fetch analytics data";
      
      if (error.response) {
        // Server responded with error status
        if (error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.status === 404) {
          errorMessage = "No data found for the specified filters";
        } else {
          errorMessage = `Request failed with status code ${error.response.status}`;
        }
      } else if (error.request) {
        // Network error
        errorMessage = "Network error - please check your connection";
      } else {
        // Other error
        errorMessage = error.message || "An unexpected error occurred";
      }
      
      setAnalyticsError(errorMessage);
      
      // For now, use the sample data you provided
      const sampleData = {
        insights: {
          executive_summary: {
            key_findings: [
              "Diabetes cases in Weija Health Facility (Kasoa) show a higher prevalence in the 36-60 age group (28 cases) followed by the 60+ age group (20 cases) during March-September 2022.",
              "Males are more affected by diabetes (33 cases) than females (18 cases) in the studied population.",
              "The majority of diabetes patients (39 out of 51) are covered by NHIA insurance, indicating a good access to healthcare but still leaving 12 uninsured individuals.",
              "Essential hypertension is a common comorbidity among diabetes patients."
            ],
            public_health_implications: [
              "The high prevalence of diabetes in the 36-60 age group could lead to reduced workforce productivity and increased healthcare costs.",
              "Uncontrolled diabetes and related complications such as neuropathy and nephropathy may put a strain on healthcare resources."
            ],
            priority_actions: [
              "Implement targeted diabetes screening programs for individuals aged 36-60, particularly males, in Kasoa.",
              "Strengthen patient education programs on diabetes management, including diet, exercise, and medication adherence.",
              "Improve access to NHIA coverage for uninsured individuals in Kasoa to ensure equitable access to diabetes care."
            ]
          },
          demographic_analysis: {
            age_distribution: {
              high_risk_groups: ["36-60", "60+"],
              age_patterns: "Diabetes prevalence increases with age, with a significant burden in the 36-60 and 60+ age groups. This suggests potential lifestyle or environmental factors contributing to the onset of diabetes in middle-aged and older adults.",
              recommendations: [
                "Develop age-specific diabetes prevention and management programs.",
                "Prioritize screening for diabetes in individuals over 35 years old."
              ]
            },
            gender_analysis: {
              gender_patterns: "Males show a higher prevalence of diabetes than females. This could be due to differences in lifestyle, occupational exposure, or biological factors.",
              risk_factors: [
                "Potential differences in lifestyle (diet, exercise) between genders",
                "Occupational exposures more common in males"
              ]
            },
            geographic_analysis: {
              hotspots: ["kasoa", "KASOA BRAODCASTING"],
              geographic_patterns: "Diabetes cases are concentrated in Kasoa and surrounding localities. This could be related to socioeconomic factors, access to healthcare, or environmental exposures.",
              environmental_factors: ["Air pollution", "Access to healthy food options"],
              hospital_analysis: {
                facility_utilization: "Weija Health Facility is the sole provider for the studied diabetes cases, implying its crucial role in diabetes management in the Kasoa region. All 51 recorded cases in the focused timeframe utilized this facility.",
                capacity_insights: [
                  "Assess Weija Health Facility's capacity to handle the increasing diabetes burden.",
                  "Evaluate the need for additional resources (staff, equipment) to provide comprehensive diabetes care."
                ],
                referral_patterns: "Data does not reflect referral patterns. Further data collection would be useful to understand if patients are being referred to other facilities for specialized care."
              }
            }
          },
          clinical_insights: {
            diagnosis_patterns: {
              common_diagnoses: [
                "E08.08 [Diabetes mellitus due to underlying condition with unspecified complications]",
                "E11.9 [Non-insulin-dependent diabetes mellitus: Without complications]"
              ],
              comorbidity_patterns: [
                "Hypertension (I10) is a frequent comorbidity",
                "Other diabetes-related complications"
              ],
              severity_indicators: [
                "Presence of complications like diabetic neuropathy and nephropathy",
                "Cases of ketoacidosis without coma"
              ]
            },
            complications: {
              frequent_complications: ["Diabetic neuropathy", "Diabetic nephropathy", "Hyperglycemia"],
              risk_factors: ["Poor glycemic control", "Hypertension"],
              prevention_strategies: [
                "Intensified glycemic control through lifestyle modifications and medication",
                "Management of hypertension"
              ]
            }
          },
          temporal_analysis: {
            seasonal_patterns: {
              peak_periods: ["2022-03", "2022-09"],
              seasonal_factors: [
                "Potential association with seasonal changes in diet or physical activity",
                "Impact of weather on medication adherence"
              ],
              forecasting_insights: "The higher incidence of diabetes cases in March and September 2022 requires closer monitoring and resource allocation during these periods in subsequent years."
            },
            trend_analysis: {
              trend_direction: "Potentially increasing (given only 7 months of data)",
              trend_factors: ["Aging population", "Increasing prevalence of obesity"],
              future_projections: "Without interventions, the number of diabetes cases is expected to rise in the coming years. This necessitates a proactive public health response to mitigate the impact of diabetes in Kasoa."
            }
          },
          healthcare_access: {
            insurance_coverage: {
              coverage_patterns: "A significant portion of diabetes patients (39/51) are covered by NHIA, indicating relatively good insurance coverage.",
              access_barriers: [
                "Uninsured individuals (12/51) may face financial barriers to accessing care.",
                "Geographic barriers to access for those in more remote locations."
              ],
              improvement_suggestions: [
                "Expand NHIA coverage to include more comprehensive diabetes care services.",
                "Implement outreach programs to enroll uninsured individuals in NHIA."
              ]
            },
            facility_utilization: {
              utilization_patterns: "Weija Health Facility is the primary healthcare provider for diabetes patients in the region.",
              capacity_implications: [
                "Assess the capacity of Weija Health Facility to meet the growing demand for diabetes care.",
                "Explore options for expanding services or establishing satellite clinics to improve access."
              ]
            }
          },
          public_health_recommendations: {
            immediate_actions: [
              {
                action: "Conduct targeted diabetes screening for adults aged 36-60 in Kasoa, focusing on men and residents of Kasoa and Kasoa Broadcasting.",
                priority: "high",
                target_population: "Adults aged 36-60, men, residents of Kasoa and Kasoa Broadcasting.",
                expected_impact: "Early detection of diabetes, leading to timely management and reduced complications."
              },
              {
                action: "Implement community-based diabetes education programs on healthy lifestyle choices, diet, exercise, and medication adherence.",
                priority: "high",
                target_population: "General population in Kasoa, with a focus on individuals at high risk of diabetes.",
                expected_impact: "Improved knowledge and awareness of diabetes prevention and management, leading to better health outcomes."
              }
            ],
            long_term_strategies: [
              {
                strategy: "Strengthen the primary healthcare system to provide comprehensive diabetes care, including regular check-ups, medication management, and complication screening.",
                timeline: "3-5 years",
                resources_needed: [
                  "Increased funding for primary healthcare services",
                  "Training of healthcare providers on diabetes management"
                ],
                success_metrics: [
                  "Reduction in the incidence of diabetes complications",
                  "Improved glycemic control among diabetes patients"
                ]
              }
            ],
            policy_implications: [
              {
                policy_area: "Health Insurance",
                recommendation: "Expand NHIA coverage to include preventive services for diabetes, such as screening and education, to encourage early detection and management.",
                stakeholders: ["Ministry of Health", "National Health Insurance Authority"]
              }
            ]
          }
        },
        metadata: {
          date_range: "2022-03:2022-09",
          year: "2022",
          disease: "diabetes",
          locality: "Kasoa",
          hospital: "Weija",
          generated_at: "2025-07-27T14:52:35.866868"
        }
      };
      
      setStructuredAnalytics(sampleData);
    } finally {
      setIsLoadingAnalytics(false);
    }
  };

  // Fetch analytics when component mounts or filters change
  const handleFetchAnalytics = () => {
    fetchStructuredAnalytics();
  };

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

  // Transform top diagnoses data for chart
  const transformedPrincipalDiagnoses = useMemo(() => {
    if (!principalDiagnosesData || !principalDiagnosesData[selectedDiseaseL]) {
      console.log("No principal diagnoses data available:", { principalDiagnosesData, selectedDiseaseL });
      return [];
    }
    
    const transformed = principalDiagnosesData[selectedDiseaseL]
      .slice(0, 10) // Show top 10 diagnoses
      .map((diagnosis, index) => ({
        id: index,
        code: diagnosis.code,
        count: parseInt(diagnosis.count) || 0, // Ensure count is a number
        description: diagnosis.description,
        // Create a shorter label for display
        shortLabel: diagnosis.code.split('[')[0].trim(),
        fullDescription: diagnosis.description
      }))
      .sort((a, b) => b.count - a.count); // Sort by count descending
    
    console.log("Transformed principal diagnoses:", transformed);
    return transformed;
  }, [principalDiagnosesData, selectedDiseaseL]);

  // Transform additional diagnoses data for chart
  const transformedAdditionalDiagnoses = useMemo(() => {
    if (!additionalDiagnosesData || !additionalDiagnosesData[selectedDiseaseL]) {
      console.log("No additional diagnoses data available:", { additionalDiagnosesData, selectedDiseaseL });
      return [];
    }
    
    const transformed = additionalDiagnosesData[selectedDiseaseL]
      .slice(0, 10) // Show top 10 diagnoses
      .map((diagnosis, index) => ({
        id: index,
        code: diagnosis.code,
        count: parseInt(diagnosis.count) || 0, // Ensure count is a number
        description: diagnosis.description,
        // Create a shorter label for display
        shortLabel: diagnosis.code.split('[')[0].trim(),
        fullDescription: diagnosis.description
      }))
      .sort((a, b) => b.count - a.count); // Sort by count descending
    
    console.log("Transformed additional diagnoses:", transformed);
    return transformed;
  }, [additionalDiagnosesData, selectedDiseaseL]);

  // Transform age distribution data for chart
  const transformedAgeDistribution = useMemo(() => {
    if (!ageDistributionData || !ageDistributionData[selectedDiseaseL]) {
      console.log("No age distribution data available:", { ageDistributionData, selectedDiseaseL });
      return [];
    }
    
    const ageData = ageDistributionData[selectedDiseaseL];
    const transformed = Object.entries(ageData).map(([age, count]) => ({
      age: age,
      cases: parseInt(count) || 0
    }));
    
    console.log("Transformed age distribution:", transformed);
    return transformed;
  }, [ageDistributionData, selectedDiseaseL]);

  // Transform sex distribution data for chart
  const transformedSexDistribution = useMemo(() => {
    if (!sexDistributionData || !sexDistributionData[selectedDiseaseL]) {
      console.log("No sex distribution data available:", { sexDistributionData, selectedDiseaseL });
      return [];
    }
    
    const sexData = sexDistributionData[selectedDiseaseL];
    const transformed = Object.entries(sexData).map(([sex, count]) => ({
      sex: sex,
      cases: parseInt(count) || 0
    }));
    
    console.log("Transformed sex distribution:", transformed);
    return transformed;
  }, [sexDistributionData, selectedDiseaseL]);

  // Transform localities trend data for chart
  const transformedLocalitiesTrend = useMemo(() => {
    if (!localitiesTrendData || !localitiesTrendData.labels || !localitiesTrendData.datasets) {
      console.log("No localities trend data available:", { localitiesTrendData });
      return [];
    }
    
    const { labels, datasets } = localitiesTrendData;
    
    // Transform to Recharts format: array of objects with month and locality data
    const transformed = labels.map((label, index) => {
      const dataPoint = { month: label };
      
      // Add each locality's data for this month
      datasets.forEach(dataset => {
        dataPoint[dataset.label] = dataset.data[index] || 0;
      });
      
      return dataPoint;
    });
    
    console.log("Transformed localities trend:", transformed);
    return transformed;
  }, [localitiesTrendData]);

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

  // Search state for localities
  const [localitySearchTerm, setLocalitySearchTerm] = useState('');

  // Filter localities based on search term
  const filteredLocalities = useMemo(() => {
    if (!localities?.data || localities.data.length === 0) return [];
    
    const allLocalities = localities.data[0]?.localities || [];
    
    if (!localitySearchTerm.trim()) return allLocalities;
    
    return allLocalities.filter(locality => 
      locality.toLowerCase().includes(localitySearchTerm.toLowerCase())
    );
  }, [localities, localitySearchTerm]);

  // Custom tooltip for principal diagnoses
  const PrincipalDiagnosesTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length && payload[0].payload) {
      const d = payload[0].payload;
      return (
        <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-xs max-w-xs">
          <div className="font-semibold text-slate-800 mb-1">{d.shortLabel}</div>
          <div className="mb-1 text-slate-600">{d.fullDescription}</div>
          <div className="text-slate-700"><span className="font-medium">Count:</span> {d.count}</div>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for additional diagnoses
  const AdditionalDiagnosesTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length && payload[0].payload) {
      const d = payload[0].payload;
      return (
        <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-xs max-w-xs">
          <div className="font-semibold text-slate-800 mb-1">{d.shortLabel}</div>
          <div className="mb-1 text-slate-600">{d.fullDescription}</div>
          <div className="text-slate-700"><span className="font-medium">Count:</span> {d.count}</div>
        </div>
      );
    }
    return null;
  };

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
            {/* <div className="flex items-center space-x-2 bg-blue-50 border border-blue-200 px-3 py-2 rounded-lg">
              <Users className="h-4 w-4 text-blue-600" />
              <span className="text-blue-700 font-semibold text-sm">Weija Hospital Data</span>
            </div> */}
            {/* Hospital Selection */}
          <Select
            value={selectedHospital}
            onValueChange={handleHospitalChange}
          >
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Select Hospital" />
            </SelectTrigger>
            <SelectContent>
              {isHospitalsLoading ? (
                <SelectItem value="loading" disabled>
                  Loading hospitals...
                </SelectItem>
              ) : (
                <>
                  <SelectItem value="all">All Hospitals</SelectItem>
                  {hospitals?.data?.find(
                    (hospital) => hospital.name === "Weija Hospital"
                  ) && <SelectItem value="weija">Weija Hospital</SelectItem>}
                  {Array.isArray(hospitals?.data) &&
                    hospitals.data
                      .filter((hospital) => hospital.name !== "Weija Hospital")
                      .map((hospital) => (
                        <SelectItem
                          key={hospital.id}
                          value={hospital.slug}
                        >
                          {hospital.name}
                        </SelectItem>
                      ))}
                </>
              )}
            </SelectContent>
          </Select>
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
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
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

              <DateRangePicker
                onDateRangeChange={handleCustomDateRangeChange}
                availableYears={finalAvailableYears}
                placeholder="Custom Range"
                className="w-48"
              />
            </div>
            
            {/* Show selected date range */}
            {customDateRange && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium text-blue-700">Selected Date Range:</span>
                  <span className="text-sm text-blue-600">{customDateRange}</span>
                  {selectedDateRangeObj && (
                    <span className="text-xs text-blue-500">
                      ({selectedDateRangeObj.from?.toLocaleDateString()} - {selectedDateRangeObj.to?.toLocaleDateString()})
                    </span>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Disease Comparison Controls */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100 rounded-lg hover:shadow-lg transition-all duration-300">
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

        {/* Dropdowns */}
        <div className="flex items-center space-x-4 w-full justify-end">
          <DateRangePicker
            onDateRangeChange={handleCustomDateRangeChange}
            availableYears={finalAvailableYears}
            placeholder="Custom Range"
            className="w-max-content"
          />

          {/* Locality for the hospital */}
          <Select
            value={selectedLocality}
            onValueChange={handleLocalityChange}
          >
            <SelectTrigger className="w-[250px]">
              <SelectValue placeholder="Select Locality" />
            </SelectTrigger>
            <SelectContent onCloseAutoFocus={(e) => e.preventDefault()}>
              {/* Search Input */}
              <div className="sticky top-0 z-10 bg-white border-b border-gray-200 p-2">
                <div className="relative">
                  <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search localities..."
                    value={localitySearchTerm}
                    onChange={(e) => setLocalitySearchTerm(e.target.value)}
                    onKeyDown={(e) => e.stopPropagation()}
                    onMouseDown={(e) => e.stopPropagation()}
                    className="w-full pl-8 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {isLocalitiesLoading && !localities?.data ? (
                <SelectItem value="loading" disabled>
                  Loading localities...
                </SelectItem>
              ) : (
                <>
                  <SelectItem value="all">All Localities</SelectItem>
                  {filteredLocalities.map((locality, index) => (
                    <SelectItem
                      key={`${locality}-${index}`}
                      value={locality}
                    >
                      {locality}
                    </SelectItem>
                  ))}
                  {localitySearchTerm && filteredLocalities.length === 0 && (
                    <div className="px-2 py-2 text-sm text-gray-500 text-center">
                      No localities found for "{localitySearchTerm}"
                    </div>
                  )}
                </>
              )}
            </SelectContent>
          </Select>

          {/* Disease Selection for Regional Chart */}
          <Select value={selectedDisease} onValueChange={handleDiseaseChange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select Disease" />
            </SelectTrigger>
            <SelectContent searchable searchPlaceholder="Search diseases...">
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

        {/* AI Insights Placeholder */}
        <Card className="shadow-lg border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <Brain className="h-4 w-4 text-white" />
              </div>
              <span className="text-slate-800">AI-Powered Analytics</span>
              <Button
                size="sm"
                onClick={handleFetchAnalytics}
                disabled={isLoadingAnalytics}
                className="ml-auto"
              >
                {isLoadingAnalytics ? (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                {isLoadingAnalytics ? "Loading..." : "Generate Insights"}
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            {analyticsError && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="h-4 w-4 text-red-500 mt-0.5" />
                  <div className="flex-1">
                    <div className="text-red-700 font-medium mb-2">Error: {analyticsError}</div>
                    <div className="text-red-600 text-sm">
                      <p>Please check your filter selections:</p>
                      <ul className="mt-1 space-y-1">
                        <li>• Hospital: {selectedHospital}</li>
                        <li>• Year: {selectedDiseaseYear}</li>
                        <li>• Disease: {selectedDisease}</li>
                        <li>• Locality: {selectedLocality}</li>
                        {customDateRange && <li>• Date Range: {customDateRange}</li>}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {!structuredAnalytics && !isLoadingAnalytics && (
              <div className="bg-white/50 rounded-lg p-6 border border-blue-200">
                <p className="text-slate-600 leading-relaxed">
                  Click "Generate Insights" to get AI-powered predictions, anomaly detection, and comprehensive analysis of your health data.
                </p>
                {customDateRange && (
                  <div className="mt-4 p-3 bg-blue-100 border border-blue-300 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-700">Will analyze data for:</span>
                      <span className="text-sm text-blue-600">{customDateRange}</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {isLoadingAnalytics && (
              <div className="bg-white/50 rounded-lg p-6 border border-blue-200">
                <div className="flex items-center space-x-3">
                  <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
                  <span className="text-slate-600">Generating AI insights...</span>
                </div>
              </div>
            )}

            {structuredAnalytics && !isLoadingAnalytics && (
              <div className="space-y-6">
                {/* Date Range Indicator */}
                {customDateRange && (
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-700">Analysis Period:</span>
                      <span className="text-sm text-blue-600">{customDateRange}</span>
                      {selectedDateRangeObj && (
                        <span className="text-xs text-blue-500">
                          ({selectedDateRangeObj.from?.toLocaleDateString()} - {selectedDateRangeObj.to?.toLocaleDateString()})
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Scrollable Content Container */}
                <div className="bg-white rounded-lg border border-blue-200 overflow-hidden">
                  <div className="h-96 overflow-y-auto p-6 space-y-6">
                    {/* Executive Summary */}
                    <div className="bg-white rounded-lg p-6 border border-blue-200">
                      <div className="flex items-center space-x-2 mb-4">
                        <Target className="h-5 w-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-slate-800">Executive Summary</h3>
                      </div>
                      
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Key Findings */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Key Findings</h4>
                          <ul className="space-y-2">
                            {structuredAnalytics.insights.executive_summary.key_findings.map((finding, index) => (
                              <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                                <span>{finding}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Public Health Implications */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Public Health Implications</h4>
                          <ul className="space-y-2">
                            {structuredAnalytics.insights.executive_summary.public_health_implications.map((implication, index) => (
                              <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                                <span>{implication}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Priority Actions */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Priority Actions</h4>
                          <ul className="space-y-2">
                            {structuredAnalytics.insights.executive_summary.priority_actions.map((action, index) => (
                              <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                                <span>{action}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Demographic Analysis */}
                    <div className="bg-white rounded-lg p-6 border border-blue-200">
                      <div className="flex items-center space-x-2 mb-4">
                        <Users className="h-5 w-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-slate-800">Demographic Analysis</h3>
                      </div>
                      
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Age Distribution */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Age Distribution</h4>
                          <div className="space-y-3">
                            <p className="text-sm text-slate-600">{structuredAnalytics.insights.demographic_analysis.age_distribution.age_patterns}</p>
                            <div>
                              <span className="text-sm font-medium text-slate-700">High Risk Groups: </span>
                              <span className="text-sm text-slate-600">{structuredAnalytics.insights.demographic_analysis.age_distribution.high_risk_groups.join(", ")}</span>
                            </div>
                            <div>
                              <span className="text-sm font-medium text-slate-700">Recommendations:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.demographic_analysis.age_distribution.recommendations.map((rec, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{rec}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>

                        {/* Gender Analysis */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Gender Analysis</h4>
                          <div className="space-y-3">
                            <p className="text-sm text-slate-600">{structuredAnalytics.insights.demographic_analysis.gender_analysis.gender_patterns}</p>
                            <div>
                              <span className="text-sm font-medium text-slate-700">Risk Factors:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.demographic_analysis.gender_analysis.risk_factors.map((factor, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-purple-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{factor}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Clinical Insights */}
                    <div className="bg-white rounded-lg p-6 border border-blue-200">
                      <div className="flex items-center space-x-2 mb-4">
                        <ActivityIcon className="h-5 w-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-slate-800">Clinical Insights</h3>
                      </div>
                      
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Diagnosis Patterns */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Diagnosis Patterns</h4>
                          <div className="space-y-3">
                            <div>
                              <span className="text-sm font-medium text-slate-700">Common Diagnoses:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.clinical_insights.diagnosis_patterns.common_diagnoses.map((diagnosis, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-red-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{diagnosis}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <span className="text-sm font-medium text-slate-700">Comorbidity Patterns:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.clinical_insights.diagnosis_patterns.comorbidity_patterns.map((pattern, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{pattern}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>

                        {/* Complications */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Complications & Prevention</h4>
                          <div className="space-y-3">
                            <div>
                              <span className="text-sm font-medium text-slate-700">Frequent Complications:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.clinical_insights.complications.frequent_complications.map((complication, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-red-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{complication}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <span className="text-sm font-medium text-slate-700">Prevention Strategies:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.clinical_insights.complications.prevention_strategies.map((strategy, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{strategy}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Temporal Analysis */}
                    <div className="bg-white rounded-lg p-6 border border-blue-200">
                      <div className="flex items-center space-x-2 mb-4">
                        <Clock className="h-5 w-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-slate-800">Temporal Analysis</h3>
                      </div>
                      
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Seasonal Patterns */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Seasonal Patterns</h4>
                          <div className="space-y-3">
                            <div>
                              <span className="text-sm font-medium text-slate-700">Peak Periods: </span>
                              <span className="text-sm text-slate-600">{structuredAnalytics.insights.temporal_analysis.seasonal_patterns.peak_periods.join(", ")}</span>
                            </div>
                            <p className="text-sm text-slate-600">{structuredAnalytics.insights.temporal_analysis.seasonal_patterns.forecasting_insights}</p>
                            <div>
                              <span className="text-sm font-medium text-slate-700">Seasonal Factors:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.temporal_analysis.seasonal_patterns.seasonal_factors.map((factor, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{factor}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>

                        {/* Trend Analysis */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Trend Analysis</h4>
                          <div className="space-y-3">
                            <div>
                              <span className="text-sm font-medium text-slate-700">Trend Direction: </span>
                              <span className="text-sm text-slate-600">{structuredAnalytics.insights.temporal_analysis.trend_analysis.trend_direction}</span>
                            </div>
                            <p className="text-sm text-slate-600">{structuredAnalytics.insights.temporal_analysis.trend_analysis.future_projections}</p>
                            <div>
                              <span className="text-sm font-medium text-slate-700">Trend Factors:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.temporal_analysis.trend_analysis.trend_factors.map((factor, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-purple-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{factor}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Healthcare Access */}
                    <div className="bg-white rounded-lg p-6 border border-blue-200">
                      <div className="flex items-center space-x-2 mb-4">
                        <Shield className="h-5 w-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-slate-800">Healthcare Access</h3>
                      </div>
                      
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Insurance Coverage */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Insurance Coverage</h4>
                          <div className="space-y-3">
                            <p className="text-sm text-slate-600">{structuredAnalytics.insights.healthcare_access.insurance_coverage.coverage_patterns}</p>
                            <div>
                              <span className="text-sm font-medium text-slate-700">Access Barriers:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.healthcare_access.insurance_coverage.access_barriers.map((barrier, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-red-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{barrier}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <span className="text-sm font-medium text-slate-700">Improvement Suggestions:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.healthcare_access.insurance_coverage.improvement_suggestions.map((suggestion, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{suggestion}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>

                        {/* Facility Utilization */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Facility Utilization</h4>
                          <div className="space-y-3">
                            <p className="text-sm text-slate-600">{structuredAnalytics.insights.healthcare_access.facility_utilization.utilization_patterns}</p>
                            <div>
                              <span className="text-sm font-medium text-slate-700">Capacity Implications:</span>
                              <ul className="mt-1 space-y-1">
                                {structuredAnalytics.insights.healthcare_access.facility_utilization.capacity_implications.map((implication, index) => (
                                  <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                    <div className="w-1 h-1 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                                    <span>{implication}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Public Health Recommendations */}
                    <div className="bg-white rounded-lg p-6 border border-blue-200">
                      <div className="flex items-center space-x-2 mb-4">
                        <Lightbulb className="h-5 w-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-slate-800">Public Health Recommendations</h3>
                      </div>
                      
                      <div className="space-y-6">
                        {/* Immediate Actions */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Immediate Actions</h4>
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            {structuredAnalytics.insights.public_health_recommendations.immediate_actions.map((action, index) => (
                              <div key={index} className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                                <div className="flex items-start space-x-2 mb-2">
                                  <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${action.priority === 'high' ? 'bg-red-500' : 'bg-orange-500'}`} />
                                  <span className="text-sm font-medium text-slate-700">{action.action}</span>
                                </div>
                                <div className="text-xs text-slate-600 space-y-1">
                                  <div><span className="font-medium">Target:</span> {action.target_population}</div>
                                  <div><span className="font-medium">Impact:</span> {action.expected_impact}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Long-term Strategies */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Long-term Strategies</h4>
                          {structuredAnalytics.insights.public_health_recommendations.long_term_strategies.map((strategy, index) => (
                            <div key={index} className="bg-green-50 rounded-lg p-4 border border-green-200 mb-3">
                              <div className="flex items-start space-x-2 mb-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                                <span className="text-sm font-medium text-slate-700">{strategy.strategy}</span>
                              </div>
                              <div className="text-xs text-slate-600 space-y-1">
                                <div><span className="font-medium">Timeline:</span> {strategy.timeline}</div>
                                <div><span className="font-medium">Resources Needed:</span></div>
                                <ul className="ml-4 space-y-1">
                                  {strategy.resources_needed.map((resource, idx) => (
                                    <li key={idx} className="flex items-start space-x-2">
                                      <div className="w-1 h-1 bg-green-500 rounded-full mt-1.5 flex-shrink-0" />
                                      <span>{resource}</span>
                                    </li>
                                  ))}
                                </ul>
                                <div><span className="font-medium">Success Metrics:</span></div>
                                <ul className="ml-4 space-y-1">
                                  {strategy.success_metrics.map((metric, idx) => (
                                    <li key={idx} className="flex items-start space-x-2">
                                      <div className="w-1 h-1 bg-green-500 rounded-full mt-1.5 flex-shrink-0" />
                                      <span>{metric}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Policy Implications */}
                        <div>
                          <h4 className="font-medium text-slate-700 mb-3">Policy Implications</h4>
                          {structuredAnalytics.insights.public_health_recommendations.policy_implications.map((policy, index) => (
                            <div key={index} className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                              <div className="flex items-start space-x-2 mb-2">
                                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0" />
                                <span className="text-sm font-medium text-slate-700">{policy.policy_area}</span>
                              </div>
                              <p className="text-sm text-slate-600 mb-2">{policy.recommendation}</p>
                              <div className="text-xs text-slate-600">
                                <span className="font-medium">Stakeholders:</span> {policy.stakeholders.join(", ")}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Metadata */}
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <div className="flex items-center space-x-4">
                      <span>Generated: {new Date(structuredAnalytics.metadata.generated_at).toLocaleString()}</span>
                      <span>Date Range: {structuredAnalytics.metadata.date_range}</span>
                      <span>Disease: {structuredAnalytics.metadata.disease}</span>
                      <span>Hospital: {structuredAnalytics.metadata.hospital}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>



        {/* Hotspots Table */}
        {/* <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
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
        </Card> */}

        {/* Demographic Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Cases by Age Group - {selectedDiseaseYear}</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              {isAgeDistributionDataLoading ? (
                <div className="flex items-center justify-center h-[250px]">
                  <div className="text-slate-500">Loading age distribution data...</div>
                </div>
              ) : transformedAgeDistribution.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={transformedAgeDistribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="age" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip 
                      formatter={(value, name) => [value, "Cases"]}
                      labelFormatter={(label) => `Age Group: ${label}`}
                    />
                    <Bar dataKey="cases" fill="#6366f1" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[250px]">
                  <div className="text-slate-500">No age distribution data available</div>
                </div>
              )}
            </CardContent>
          </Card>
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Cases by Sex - {selectedDiseaseYear}</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              {isSexDistributionDataLoading ? (
                <div className="flex items-center justify-center h-[250px]">
                  <div className="text-slate-500">Loading sex distribution data...</div>
                </div>
              ) : transformedSexDistribution.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie 
                      data={transformedSexDistribution} 
                      dataKey="cases" 
                      nameKey="sex" 
                      cx="50%" 
                      cy="50%" 
                      outerRadius={80} 
                      fill="#22c55e" 
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {transformedSexDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? "#22c55e" : "#ef4444"} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value, name) => [value, "Cases"]}
                      labelFormatter={(label) => `Sex: ${label}`}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[250px]">
                  <div className="text-slate-500">No sex distribution data available</div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Diagnosis Patterns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Top Principal Diagnoses - {selectedDiseaseYear}</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              {isPrincipalDiagnosesDataLoading ? (
                <div className="flex items-center justify-center h-[350px]">
                  <div className="text-slate-500">Loading diagnoses data...</div>
                </div>
              ) : transformedPrincipalDiagnoses.length > 0 ? (
                <div className="mt-6">
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart 
                      data={transformedPrincipalDiagnoses}
                      margin={{ top: 20, right: 30, left: 30, bottom: 80 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis 
                        dataKey="shortLabel" 
                        stroke="#64748b" 
                        fontSize={12}
                        angle={-40}
                        textAnchor="end"
                        interval={0}
                        height={60}
                      />
                      <YAxis 
                        stroke="#64748b" 
                        fontSize={12}
                      />
                      <Tooltip 
                        content={<PrincipalDiagnosesTooltip />}
                      />
                      <Bar 
                        dataKey="count" 
                        fill="#ef4444"
                        name="Count"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="flex items-center justify-center h-[350px]">
                  <div className="text-slate-500">No diagnoses data available</div>
                </div>
              )}
            </CardContent>
          </Card>
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Top Additional Diagnoses - {selectedDiseaseYear}</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              {isAdditionalDiagnosesDataLoading ? (
                <div className="flex items-center justify-center h-[350px]">
                  <div className="text-slate-500">Loading diagnoses data...</div>
                </div>
              ) : transformedAdditionalDiagnoses.length > 0 ? (
                <div className="mt-6">
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart 
                      data={transformedAdditionalDiagnoses}
                      margin={{ top: 20, right: 30, left: 30, bottom: 80 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis 
                        dataKey="shortLabel" 
                        stroke="#64748b" 
                        fontSize={12}
                        angle={-40}
                        textAnchor="end"
                        interval={0}
                        height={60}
                      />
                      <YAxis 
                        stroke="#64748b" 
                        fontSize={12}
                      />
                      <Tooltip 
                        content={<AdditionalDiagnosesTooltip />}
                      />
                      <Bar 
                        dataKey="count" 
                        fill="#6366f1"
                        name="Count"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="flex items-center justify-center h-[350px]">
                  <div className="text-slate-500">No diagnoses data available</div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* NHIA & Pregnancy Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>NHIA Status - {selectedDiseaseYear}</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  {isNHIAStatusDataLoading ? (
                    <text x="50%" y="50%" textAnchor="middle" dy=".3em" fill="#666">
                      Loading...
                    </text>
                  ) : nhiaStatusData?.[selectedDiseaseL]?.yes && nhiaStatusData?.[selectedDiseaseL]?.no ? (
                    <Pie
                      data={NHIAStatusDistribution(nhiaStatusData?.[selectedDiseaseL]?.yes, nhiaStatusData?.[selectedDiseaseL]?.no)}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {NHIAStatusDistribution(nhiaStatusData?.[selectedDiseaseL]?.yes, nhiaStatusData?.[selectedDiseaseL]?.no).map((entry, index) => (
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
                {/* <PieChart>
                  <Pie data={nhiaStatusData} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={80} fill="#6366f1" label />
                  <Tooltip />
                </PieChart> */}
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="pb-4">
              <CardTitle>Pregnancy Status - {selectedDiseaseYear}</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  {isPregnancyStatusDataLoading ? (
                    <text x="50%" y="50%" textAnchor="middle" dy=".3em" fill="#666">
                      Loading...
                    </text>
                  ) : pregnancyStatusData?.[selectedDiseaseL]?.yes && pregnancyStatusData?.[selectedDiseaseL]?.no ? (
                    <Pie
                      data={PregnancyStatusDistribution(pregnancyStatusData?.[selectedDiseaseL]?.yes, pregnancyStatusData?.[selectedDiseaseL]?.no)}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {PregnancyStatusDistribution(pregnancyStatusData?.[selectedDiseaseL]?.yes, pregnancyStatusData?.[selectedDiseaseL]?.no).map((entry, index) => (
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
                {/* <PieChart>
                  <Pie data={pregnancyStatusData} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={80} fill="#22c55e" label />
                  <Tooltip />
                </PieChart> */}
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Trends by Locality */}
        <Card className="shadow-lg border-slate-200 hover:shadow-xl transition-shadow duration-300">
          <CardHeader className="pb-4">
            <CardTitle>Trends by Locality - {selectedDiseaseYear}</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            {isLocalitiesTrendDataLoading ? (
              <div className="flex items-center justify-center h-[300px]">
                <div className="text-slate-500">Loading localities trend data...</div>
              </div>
            ) : transformedLocalitiesTrend.length > 0 && localitiesTrendData?.datasets ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={transformedLocalitiesTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip 
                    formatter={(value, name) => [value, "Cases"]}
                    labelFormatter={(label) => `Month: ${label}`}
                  />
                  <Legend />
                  {localitiesTrendData.datasets.map((dataset, index) => (
                    <Line 
                      key={dataset.label}
                      type="monotone" 
                      dataKey={dataset.label} 
                      stroke={`hsl(${(index * 137.5) % 360}, 70%, 50%)`}
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px]">
                <div className="text-slate-500">No localities trend data available</div>
              </div>
            )}
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
