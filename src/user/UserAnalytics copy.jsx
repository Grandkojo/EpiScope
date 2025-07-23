import { useState } from "react"
import { Badge } from "../components/ui/badge"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select"
import { AlertTriangle, MapPin, Users, TrendingUp, Filter } from "lucide-react"
import { useDiseaseYears } from "../data/all_years";
import { useDiseases } from "../data/all_diseases";
// Dummy data for disease hotspots
const diseaseData = [
    {
        id: 1,
        disease: "Malaria",
        region: "Northern Region",
        city: "Tamale",
        cases: 1250,
        severity: "high",
        coordinates: { x: 50, y: 25 }, // Northern Ghana
        color: "#ef4444",
        trend: "increasing",
    },
    {
        id: 2,
        disease: "Cholera",
        region: "Greater Accra",
        city: "Accra",
        cases: 89,
        severity: "medium",
        coordinates: { x: 58, y: 75 }, // Accra area
        color: "#f59e0b",
        trend: "stable",
    },
    {
        id: 3,
        disease: "Yellow Fever",
        region: "Ashanti Region",
        city: "Kumasi",
        cases: 45,
        severity: "low",
        coordinates: { x: 45, y: 55 }, // Central Ghana (Kumasi)
        color: "#eab308",
        trend: "decreasing",
    },
    {
        id: 4,
        disease: "Dengue",
        region: "Western Region",
        city: "Takoradi",
        cases: 156,
        severity: "medium",
        coordinates: { x: 25, y: 70 }, // Western coast
        color: "#f97316",
        trend: "increasing",
    },
    {
        id: 5,
        disease: "Meningitis",
        region: "Upper East",
        city: "Bolgatanga",
        cases: 78,
        severity: "high",
        coordinates: { x: 65, y: 15 }, // Upper East
        color: "#dc2626",
        trend: "stable",
    },
    {
        id: 6,
        disease: "Typhoid",
        region: "Central Region",
        city: "Cape Coast",
        cases: 234,
        severity: "medium",
        coordinates: { x: 40, y: 75 }, // Central coast
        color: "#ea580c",
        trend: "increasing",
    },
    {
        id: 7,
        disease: "Malaria",
        region: "Volta Region",
        city: "Ho",
        cases: 167,
        severity: "medium",
        coordinates: { x: 70, y: 65 }, // Eastern Ghana
        color: "#ef4444",
        trend: "decreasing",
    },
]

const regions = [
    "All Regions",
    "Northern Region",
    "Greater Accra",
    "Ashanti Region",
    "Western Region",
    "Upper East",
    "Central Region",
    "Volta Region",
]

export default function GhanaHotspotDashboard() {
    const [selectedRegion, setSelectedRegion] = useState("All Regions")
    const [selectedHotspot, setSelectedHotspot] = useState(null)
    const [selectedDisease, setSelectedDisease] = useState(() => {
        return localStorage.getItem("selectedDisease") || "Diabetes";
    });

    const filteredData = diseaseData.filter((item) => {
        const regionMatch = selectedRegion === "All Regions" || item.region === selectedRegion
        const diseaseMatch = selectedDisease === "All Diseases" || item.disease === selectedDisease
        return regionMatch && diseaseMatch
    })

    const { data: diseases, isLoading: isDiseasesLoading, error } = useDiseases();

    const selectedDiseaseId = diseases?.find(
        (disease) => disease.disease_name === selectedDisease
    )?.id;

    const handleDiseaseChange = (value) => {
        setSelectedDisease(value);
        localStorage.setItem("selectedDisease", value);
    };

    const handleDiseaseYearChange = (value) => {
        setSelectedDiseaseYear(value);
        localStorage.setItem("selectedDiseaseYear", value);
    };

    const {
        data: diseaseYears,
        isLoading: isDiseaseYearsLoading,
        error: isDiseaseYearsError,
    } = useDiseaseYears(selectedDiseaseId);

    const [selectedDiseaseYear, setSelectedDiseaseYear] = useState(() => {
        return (
            localStorage.getItem("selectedDiseaseYear") ||
            String(new Date().getFullYear())
        );
    });

    const totalCases = filteredData.reduce((sum, item) => sum + item.cases, 0)
    const highSeverityCount = filteredData.filter((item) => item.severity === "high").length

    const getSeverityColor = (severity) => {
        switch (severity) {
            case "high":
                return "bg-red-500"
            case "medium":
                return "bg-orange-500"
            case "low":
                return "bg-yellow-500"
            default:
                return "bg-gray-500"
        }
    }

    const getTrendIcon = (trend) => {
        switch (trend) {
            case "increasing":
                return "↗️"
            case "decreasing":
                return "↘️"
            case "stable":
                return "➡️"
            default:
                return "➡️"
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 p-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Ghana Disease Hotspot Monitor</h1>
                    <p className="text-gray-600">Real-time monitoring of disease outbreaks across Ghana's regions</p>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600">Total Cases</p>
                                    <p className="text-2xl font-bold">{totalCases.toLocaleString()}</p>
                                </div>
                                <Users className="w-8 h-8 text-blue-500" />
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600">Active Hotspots</p>
                                    <p className="text-2xl font-bold">{filteredData.length}</p>
                                </div>
                                <MapPin className="w-8 h-8 text-green-500" />
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600">High Severity</p>
                                    <p className="text-2xl font-bold">{highSeverityCount}</p>
                                </div>
                                <AlertTriangle className="w-8 h-8 text-red-500" />
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600">Regions Affected</p>
                                    <p className="text-2xl font-bold">{new Set(filteredData.map((item) => item.region)).size}</p>
                                </div>
                                <TrendingUp className="w-8 h-8 text-purple-500" />
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Map Section */}
                    <div className="lg:col-span-2">
                        <Card>
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <CardTitle>Hotspot Map</CardTitle>
                                    <div className="flex gap-2">
                                        <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                                            <SelectTrigger className="w-40">
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {regions.map((region) => (
                                                    <SelectItem key={region} value={region}>
                                                        {region}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        {/* Diseases */}
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
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="relative bg-blue-50 rounded-lg p-4" style={{ height: "700px" }}>
                                    {/* More Accurate Ghana Map Outline */}
                                    <svg
                                        viewBox="0 0 100 100"
                                        className="absolute inset-0 w-full h-full"
                                        style={{ filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.1))" }}
                                    >
                                        {/* Ghana country outline - more accurate shape */}
                                        <path
                                            d="M25 10 L75 10 L80 15 L85 20 L85 25 L80 30 L75 35 L70 40 L75 45 L80 50 L85 55 L85 60 L80 65 L75 70 L70 75 L65 80 L60 85 L55 90 L50 92 L45 90 L40 92 L35 90 L30 85 L25 80 L20 75 L15 70 L10 65 L15 60 L20 55 L25 50 L20 45 L25 40 L20 35 L15 30 L10 25 L15 20 L20 15 L25 10 Z"
                                            fill="#e0f2fe"
                                            stroke="#0369a1"
                                            strokeWidth="0.8"
                                        />

                                        {/* Regional boundaries - All 16 regions */}
                                        {/* Northern tier boundaries */}
                                        <line x1="15" y1="25" x2="85" y2="25" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
                                        <line x1="35" y1="10" x2="35" y2="25" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
                                        <line x1="55" y1="10" x2="55" y2="25" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

                                        {/* Second tier boundaries */}
                                        <line x1="15" y1="40" x2="85" y2="40" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
                                        <line x1="30" y1="25" x2="30" y2="40" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
                                        <line x1="60" y1="25" x2="60" y2="40" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

                                        {/* Third tier boundaries */}
                                        <line x1="20" y1="55" x2="80" y2="55" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
                                        <line x1="35" y1="40" x2="35" y2="55" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
                                        <line x1="50" y1="40" x2="50" y2="55" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
                                        <line x1="65" y1="40" x2="65" y2="55" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

                                        {/* Fourth tier boundaries */}
                                        <line x1="25" y1="70" x2="75" y2="70" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />
                                        <line x1="45" y1="55" x2="45" y2="70" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

                                        {/* Southern tier boundaries */}
                                        <line x1="55" y1="70" x2="55" y2="92" stroke="#64748b" strokeWidth="0.4" strokeDasharray="3,2" />

                                        {/* Lake Volta (simplified) */}
                                        <ellipse cx="65" cy="55" rx="6" ry="12" fill="#3b82f6" opacity="0.3" />

                                        {/* Regional labels - All 16 regions */}
                                        {/* Northern tier */}
                                        <text x="25" y="18" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            <tspan x="25" dy="0">
                                                Upper
                                            </tspan>
                                            <tspan x="25" dy="3">
                                                West
                                            </tspan>
                                        </text>
                                        <text x="45" y="18" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            <tspan x="45" dy="0">
                                                Upper
                                            </tspan>
                                            <tspan x="45" dy="3">
                                                East
                                            </tspan>
                                        </text>
                                        <text x="70" y="18" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            <tspan x="70" dy="0">
                                                North
                                            </tspan>
                                            <tspan x="70" dy="3">
                                                East
                                            </tspan>
                                        </text>

                                        {/* Second tier */}
                                        <text x="22" y="33" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Savannah
                                        </text>
                                        <text x="45" y="33" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Northern
                                        </text>
                                        <text x="72" y="33" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Oti
                                        </text>

                                        {/* Third tier */}
                                        <text x="27" y="48" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Bono
                                        </text>
                                        <text x="42" y="46" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            <tspan x="42" dy="0">
                                                Bono
                                            </tspan>
                                            <tspan x="42" dy="3">
                                                East
                                            </tspan>
                                        </text>
                                        <text x="57" y="48" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Ashanti
                                        </text>
                                        <text x="72" y="48" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Volta
                                        </text>

                                        {/* Fourth tier */}
                                        <text x="35" y="63" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Ahafo
                                        </text>
                                        <text x="60" y="63" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Eastern
                                        </text>

                                        {/* Southern tier */}
                                        <text x="32" y="80" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            <tspan x="32" dy="0">
                                                Western
                                            </tspan>
                                            <tspan x="32" dy="3">
                                                North
                                            </tspan>
                                        </text>
                                        <text x="32" y="86" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Western
                                        </text>
                                        <text x="47" y="82" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            Central
                                        </text>
                                        <text x="62" y="80" fontSize="2.2" fill="#374151" fontWeight="bold" textAnchor="middle">
                                            <tspan x="62" dy="0">
                                                Greater
                                            </tspan>
                                            <tspan x="62" dy="3">
                                                Accra
                                            </tspan>
                                        </text>
                                    </svg>

                                    {/* Hotspot Markers */}
                                    {filteredData.map((hotspot) => (
                                        <div
                                            key={hotspot.id}
                                            className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
                                            style={{
                                                left: `${hotspot.coordinates.x}%`,
                                                top: `${hotspot.coordinates.y}%`,
                                            }}
                                            onClick={() => setSelectedHotspot(hotspot)}
                                        >
                                            {/* Pulsing outer ring */}
                                            <div
                                                className="absolute w-8 h-8 rounded-full animate-ping opacity-30"
                                                style={{ backgroundColor: hotspot.color, left: "-4px", top: "-4px" }}
                                            />

                                            {/* Main marker */}
                                            <div
                                                className="w-4 h-4 rounded-full border-2 border-white shadow-lg relative z-10"
                                                style={{ backgroundColor: hotspot.color }}
                                            />

                                            {/* Tooltip on hover */}
                                            <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-black text-white px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-20">
                                                <div className="font-semibold">{hotspot.disease}</div>
                                                <div>
                                                    {hotspot.city} - {hotspot.cases} cases
                                                </div>
                                                <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-black"></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Legend */}
                                <div className="mt-4 flex flex-wrap gap-6">
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                                        <span className="text-sm">High Severity (500+ cases)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
                                        <span className="text-sm">Medium Severity (100-499 cases)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
                                        <span className="text-sm">Low Severity ({"<"}100 cases)</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Selected Hotspot Details */}
                        {selectedHotspot ? (
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded-full" style={{ backgroundColor: selectedHotspot.color }} />
                                        Hotspot Details
                                    </CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-3">
                                    <div>
                                        <p className="font-semibold text-lg">{selectedHotspot.disease}</p>
                                        <p className="text-gray-600">
                                            {selectedHotspot.city}, {selectedHotspot.region}
                                        </p>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span>Cases:</span>
                                        <span className="font-semibold text-lg">{selectedHotspot.cases.toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span>Severity:</span>
                                        <Badge className={getSeverityColor(selectedHotspot.severity)}>
                                            {selectedHotspot.severity.toUpperCase()}
                                        </Badge>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span>Trend:</span>
                                        <span className="flex items-center gap-1">
                                            <span>{getTrendIcon(selectedHotspot.trend)}</span>
                                            <span className="capitalize">{selectedHotspot.trend}</span>
                                        </span>
                                    </div>
                                    <div className="pt-2 space-y-2">
                                        <Button className="w-full" size="sm">
                                            View Full Report
                                        </Button>
                                        <Button
                                            variant="outline"
                                            className="w-full bg-transparent"
                                            size="sm"
                                            onClick={() => setSelectedHotspot(null)}
                                        >
                                            Close Details
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        ) : (
                            <Card>
                                <CardContent className="p-6 text-center">
                                    <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                                    <p className="text-gray-600">Click on a hotspot marker to view details</p>
                                </CardContent>
                            </Card>
                        )}

                        {/* Disease List */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Active Outbreaks</CardTitle>
                                <CardDescription>Current disease cases by location</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3 max-h-64 overflow-y-auto">
                                    {filteredData
                                        .sort((a, b) => b.cases - a.cases)
                                        .map((item) => (
                                            <div
                                                key={item.id}
                                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                                                onClick={() => setSelectedHotspot(item)}
                                            >
                                                <div className="flex items-center gap-3">
                                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                                                    <div>
                                                        <p className="font-medium text-sm">{item.disease}</p>
                                                        <p className="text-xs text-gray-600">
                                                            {item.city}, {item.region}
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className="font-semibold text-sm">{item.cases}</p>
                                                    <p className="text-xs text-gray-600">{getTrendIcon(item.trend)}</p>
                                                </div>
                                            </div>
                                        ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Quick Actions */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Quick Actions</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                <Button variant="outline" className="w-full justify-start bg-transparent">
                                    <AlertTriangle className="w-4 h-4 mr-2" />
                                    Send Alert
                                </Button>
                                <Button variant="outline" className="w-full justify-start bg-transparent">
                                    <Filter className="w-4 h-4 mr-2" />
                                    Advanced Filters
                                </Button>
                                <Button variant="outline" className="w-full justify-start bg-transparent">
                                    Export Data
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}
