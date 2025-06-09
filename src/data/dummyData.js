// Dummy data for Ghana health monitoring
export const ghanaRegions = [
  "Greater Accra",
  "Ashanti",
  "Western",
  "Eastern",
  "Northern",
  "Volta",
  "Central",
  "Upper East",
  "Upper West",
  "Brong Ahafo",
]

export const diabetesData = [
  { region: "Greater Accra", cases: 15420, population: 5455692, rate: 2.83, month: "Jan" },
  { region: "Ashanti", cases: 12890, population: 4780380, rate: 2.7, month: "Jan" },
  { region: "Western", cases: 8760, population: 2376021, rate: 3.69, month: "Jan" },
  { region: "Eastern", cases: 7340, population: 2633154, rate: 2.79, month: "Jan" },
  { region: "Northern", cases: 6890, population: 2479461, rate: 2.78, month: "Jan" },
  { region: "Volta", cases: 5670, population: 2118252, rate: 2.68, month: "Jan" },
  { region: "Central", cases: 6780, population: 2201863, rate: 3.08, month: "Jan" },
  { region: "Upper East", cases: 3450, population: 1046545, rate: 3.3, month: "Jan" },
  { region: "Upper West", cases: 2890, population: 702110, rate: 4.12, month: "Jan" },
  { region: "Brong Ahafo", cases: 7890, population: 2310983, rate: 3.41, month: "Jan" },
]

export const malariaData = [
  { region: "Greater Accra", cases: 45230, population: 5455692, rate: 8.29, month: "Jan" },
  { region: "Ashanti", cases: 67890, population: 4780380, rate: 14.2, month: "Jan" },
  { region: "Western", cases: 78960, population: 2376021, rate: 33.24, month: "Jan" },
  { region: "Eastern", cases: 56780, population: 2633154, rate: 21.56, month: "Jan" },
  { region: "Northern", cases: 89670, population: 2479461, rate: 36.16, month: "Jan" },
  { region: "Volta", cases: 43560, population: 2118252, rate: 20.57, month: "Jan" },
  { region: "Central", cases: 52340, population: 2201863, rate: 23.77, month: "Jan" },
  { region: "Upper East", cases: 34560, population: 1046545, rate: 33.02, month: "Jan" },
  { region: "Upper West", cases: 28900, population: 702110, rate: 41.16, month: "Jan" },
  { region: "Brong Ahafo", cases: 65430, population: 2310983, rate: 28.31, month: "Jan" },
]

export const monthlyTrends = [
  { month: "Jan", diabetes: 77890, malaria: 543820 },
  { month: "Feb", diabetes: 79340, malaria: 567890 },
  { month: "Mar", diabetes: 81230, malaria: 589670 },
  { month: "Apr", diabetes: 78560, malaria: 612340 },
  { month: "May", diabetes: 82340, malaria: 634560 },
  { month: "Jun", diabetes: 84670, malaria: 678900 },
  { month: "Jul", diabetes: 86890, malaria: 723450 },
  { month: "Aug", diabetes: 85430, malaria: 756780 },
  { month: "Sep", diabetes: 87650, malaria: 734560 },
  { month: "Oct", diabetes: 89230, malaria: 698760 },
  { month: "Nov", diabetes: 91340, malaria: 645230 },
  { month: "Dec", diabetes: 88760, malaria: 612890 },
]

export const hotspots = [
  {
    id: 1,
    region: "Upper West",
    lat: 10.0601,
    lng: -2.5097,
    diabetesRate: 4.12,
    malariaRate: 41.16,
    severity: "high",
    population: 702110,
  },
  {
    id: 2,
    region: "Northern",
    lat: 9.4034,
    lng: -0.8424,
    diabetesRate: 2.78,
    malariaRate: 36.16,
    severity: "high",
    population: 2479461,
  },
  {
    id: 3,
    region: "Western",
    lat: 5.1097,
    lng: -2.7974,
    diabetesRate: 3.69,
    malariaRate: 33.24,
    severity: "medium",
    population: 2376021,
  },
  {
    id: 4,
    region: "Upper East",
    lat: 10.7889,
    lng: -0.8667,
    diabetesRate: 3.3,
    malariaRate: 33.02,
    severity: "medium",
    population: 1046545,
  },
  {
    id: 5,
    region: "Brong Ahafo",
    lat: 7.7167,
    lng: -2.3167,
    diabetesRate: 3.41,
    malariaRate: 28.31,
    severity: "medium",
    population: 2310983,
  },
]

export const healthMetrics = {
  totalDiabetesCases: 88760,
  totalMalariaCases: 612890,
  affectedRegions: 10,
  criticalHotspots: 5,
  monthlyGrowthDiabetes: 2.3,
  monthlyGrowthMalaria: -4.7,
  populationAtRisk: 24103461,
}
