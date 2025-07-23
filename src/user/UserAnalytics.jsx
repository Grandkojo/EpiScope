// "use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertTriangle, MapPin, Users, TrendingUp, Filter } from "lucide-react"
import { MapComponent, Coordinates } from "../components/MapComponent"
import { useRegions } from "../data/all_regions"
import { useDiseases } from "../data/all_diseases"
import { useDiseaseYears } from "../data/all_years"
import { useHotspots } from "../data/hotspots"
// Dummy data for disease hotspots
const diseaseData = [
    {
        id: 1,
        disease: "Malaria",
        region: "Northern Region",
        city: "Tamale",
        cases: 1250,
        severity: "high",
        coordinates: (() => {
            const found = Coordinates.find(item => item.name === "ET");
            return found ? { x: found.coordinates[0], y: found.coordinates[1] } : null;
        })(),
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
        coordinates: (() => {
            const found = Coordinates.find(item => item.name === "GA");
            return found ? { x: found.coordinates[0], y: found.coordinates[1] } : null;
        })(),
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
        coordinates: (() => {
            const found = Coordinates.find(item => item.name === "AS");
            return found ? { x: found.coordinates[0], y: found.coordinates[1] } : null;
        })(),
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
        coordinates: (() => {
            const found = Coordinates.find(item => item.name === "WE");
            return found ? { x: found.coordinates[0], y: found.coordinates[1] } : null;
        })(),
        color: "#f97316",
        trend: "increasing",
    },
    {
        id: 5,
        disease: "Meningitis",
        region: "Upper East Region",
        city: "Bolgatanga",
        cases: 78,
        severity: "high",
        coordinates: (() => {
            const found = Coordinates.find(item => item.name === "UE");
            return found ? { x: found.coordinates[0], y: found.coordinates[1] } : null;
        })(),
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
        coordinates: (() => {
            const found = Coordinates.find(item => item.name === "CE");
            return found ? { x: found.coordinates[0], y: found.coordinates[1] } : null;
        })(),
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
        coordinates: (() => {
            const found = Coordinates.find(item => item.name === "VO");
            return found ? { x: found.coordinates[0], y: found.coordinates[1] } : null;
        })(),
        color: "#ef4444",
        trend: "decreasing",
    },
]


export default function UserAnalytics() {
    const { data: regions, isLoading: isRegionsLoading, isError: isRegionsError } = useRegions()
    const { data: diseases, isLoading: isDiseasesLoading, isError: isDiseasesError } = useDiseases()

    const [selectedHotspot, setSelectedHotspot] = useState(null)

    const [selectedRegion, setSelectedRegion] = useState(() => {
        return localStorage.getItem("selectedRegion") || "all";
    });
    const [selectedDisease, setSelectedDisease] = useState(() => {
        return localStorage.getItem("selectedDisease") || "Diabetes";
    });

    const selectedDiseaseL = selectedDisease.toLowerCase();
    const selectedRegionL = selectedRegion.toLowerCase();
    const [selectedDiseaseYear, setSelectedDiseaseYear] = useState(() => {
        return (
            localStorage.getItem("selectedDiseaseYear") ||
            String(new Date().getFullYear())
        );
    });
    const selectedDiseaseId = diseases?.find(
        (disease) => disease.disease_name === selectedDisease
    )?.id;

    const { data: diseaseYears, isLoading: isDiseaseYearsLoading, isError: isDiseaseYearsError } = useDiseaseYears(selectedDiseaseId)

    const filteredData = diseaseData.filter((item) => {
        const regionMatch = selectedRegion === "all" || item.region === selectedRegion
        const diseaseMatch = selectedDisease === "all" || item.disease === selectedDisease
        return regionMatch && diseaseMatch
    })

    const totalCases = filteredData.reduce((sum, item) => sum + item.cases, 0)
    const highSeverityCount = filteredData.filter((item) => item.severity === "high").length
    const { data: hotspots, isLoading: isHotspotsLoading, isError: isHotspotsError } = useHotspots(selectedRegion, selectedDiseaseL, selectedDiseaseYear)

    // map the hotspots to the diseaseData
    const mappedHotspots = hotspots?.map((hotspot) => {
        hotspot.color = hotspot.severity === "high" ? "#ef4444" : hotspot.severity === "medium" ? "#f59e0b" : "#eab308"
        const foundCoordinates = Coordinates.find((item) => item.name === hotspot.code)
        hotspot.coordinates = foundCoordinates ? { x: foundCoordinates.coordinates[0], y: foundCoordinates.coordinates[1] } : null
        return hotspot
    }) || []
    console.log(mappedHotspots)

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

    const handleSelectedRegion = (value) => {
        setSelectedRegion(value);
        localStorage.setItem("selectedRegion", value);
    };

    const handleSelectedDisease = (value) => {
        setSelectedDisease(value);
        localStorage.setItem("selectedDisease", value);
    };

    const handleSelectedDiseaseYear = (value) => {
        setSelectedDiseaseYear(value);
        localStorage.setItem("selectedDiseaseYear", value);
    };
    return (
        <div className="min-h-screen bg-gray-50 p-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Ghana Disease Hotspot Monitor</h1>
                    <p className="text-gray-600">Real-time monitoring of disease outbreaks across Ghana's regions</p>

                    <div className="flex gap-2 justify-end">
                        <Select value={selectedRegion} onValueChange={handleSelectedRegion}>
                            <SelectTrigger className="w-40">
                                <SelectValue placeholder="Select Region" />
                            </SelectTrigger>
                            <SelectContent>
                                {isRegionsLoading ? (
                                    <SelectItem value="loading" disabled>Loading...</SelectItem>
                                ) : isRegionsError ? (
                                    <SelectItem value="error" disabled>Error loading regions</SelectItem>
                                ) : (
                                    <>
                                        <SelectItem value="all">All Regions</SelectItem>
                                        {Array.isArray(regions) &&
                                            regions
                                                .map((region) => (
                                                    <SelectItem
                                                        key={region}
                                                        value={region}
                                                    >
                                                        {region}
                                                    </SelectItem>
                                                ))}
                                    </>
                                )}
                            </SelectContent>
                        </Select>
                        <Select value={selectedDisease} onValueChange={handleSelectedDisease}>
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
                        <Select
                            value={selectedDiseaseYear}
                            onValueChange={handleSelectedDiseaseYear}
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

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600">Total Cases</p>
                                    {isHotspotsLoading ? (
                                        <div className="h-8 w-16 bg-gray-200 animate-pulse rounded"></div>
                                    ) : (
                                        <p className="text-2xl font-bold">
                                            {mappedHotspots.reduce((sum, hotspot) => {
                                                const casesKey = Object.keys(hotspot || {}).find(key => key.includes('cases'));
                                                const casesValue = casesKey && hotspot[casesKey] !== null && hotspot[casesKey] !== undefined 
                                                    ? hotspot[casesKey] 
                                                    : 0;
                                                return sum + casesValue;
                                            }, 0).toLocaleString()}
                                        </p>
                                    )}
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
                                    {isHotspotsLoading ? (
                                        <div className="h-8 w-16 bg-gray-200 animate-pulse rounded"></div>
                                    ) : (
                                        <p className="text-2xl font-bold">{mappedHotspots.length}</p>
                                    )}
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
                                    {isHotspotsLoading ? (
                                        <div className="h-8 w-16 bg-gray-200 animate-pulse rounded"></div>
                                    ) : (
                                        <p className="text-2xl font-bold">
                                            {mappedHotspots.filter((hotspot) => hotspot.severity === "high").length}
                                        </p>
                                    )}
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
                                    {isHotspotsLoading ? (
                                        <div className="h-8 w-16 bg-gray-200 animate-pulse rounded"></div>
                                    ) : (
                                        <p className="text-2xl font-bold">
                                            {new Set(mappedHotspots.map((hotspot) => hotspot.organisationunitname)).size}
                                        </p>
                                    )}
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
                                    <CardTitle>Ghana Disease Hotspot Map</CardTitle>
                                    {/* <div className="flex gap-2">
                                        <Select value={selectedRegion} onValueChange={handleSelectedRegion}>
                                            <SelectTrigger className="w-40">
                                                <SelectValue placeholder="Select Region" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {isRegionsLoading ? (
                                                    <SelectItem value="loading" disabled>Loading...</SelectItem>
                                                ) : isRegionsError ? (
                                                    <SelectItem value="error" disabled>Error loading regions</SelectItem>
                                                ) : (
                                                    <>
                                                        <SelectItem value="all">All Regions</SelectItem>
                                                        {Array.isArray(regions) &&
                                                            regions
                                                                .map((region) => (
                                                                    <SelectItem
                                                                        key={region}
                                                                        value={region}
                                                                    >
                                                                        {region}
                                                                    </SelectItem>
                                                                ))}
                                                    </>
                                                )}
                                            </SelectContent>
                                        </Select>
                                        <Select value={selectedDisease} onValueChange={handleSelectedDisease}>
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
                                        <Select
                                            value={selectedDiseaseYear}
                                            onValueChange={handleSelectedDiseaseYear}
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
                                    </div> */}
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="relative bg-blue-50 rounded-lg p-4" style={{ height: "700px" }}>
                                    {/* Ghana Map with SVG Markers */}
                                    <MapComponent
                                        hotspots={mappedHotspots}
                                        onMarkerClick={setSelectedHotspot}
                                        disease={selectedDisease}
                                    />
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
                                        <p className="font-semibold text-lg">{selectedDisease}</p>
                                        <p className="text-gray-600">
                                            {selectedHotspot.organisationunitname} Region
                                        </p>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span>Cases:</span>
                                        <span className="font-semibold text-lg">
                                            {(() => {
                                                const casesKey = Object.keys(selectedHotspot || {}).find(key => key.includes('cases'));
                                                const casesValue = casesKey && selectedHotspot[casesKey] !== null && selectedHotspot[casesKey] !== undefined
                                                    ? selectedHotspot[casesKey]
                                                    : selectedHotspot?.cases || 0;
                                                return casesValue.toLocaleString();
                                            })()}
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span>Severity:</span>
                                        <Badge className={getSeverityColor(selectedHotspot.severity)}>
                                            {selectedHotspot.severity.toUpperCase()}
                                        </Badge>
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
                                    {isHotspotsLoading ? (
                                        <div className="text-center text-gray-500">Loading hotspots...</div>
                                    ) : (
                                        mappedHotspots
                                            .sort((a, b) => {
                                                const aCasesKey = Object.keys(a || {}).find(key => key.includes('cases'));
                                                const bCasesKey = Object.keys(b || {}).find(key => key.includes('cases'));
                                                const aCases = aCasesKey && a[aCasesKey] !== null && a[aCasesKey] !== undefined ? a[aCasesKey] : 0;
                                                const bCases = bCasesKey && b[bCasesKey] !== null && b[bCasesKey] !== undefined ? b[bCasesKey] : 0;
                                                return bCases - aCases;
                                            })
                                            .map((hotspot) => (
                                                <div
                                                    key={`${hotspot.organisationunitname}-${hotspot.code}`}
                                                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                                                    onClick={() => setSelectedHotspot(hotspot)}
                                                >
                                                    <div className="flex items-center gap-3">
                                                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: hotspot.color }} />
                                                        <div>
                                                            <p className="font-medium text-sm">{selectedDisease}</p>
                                                            <p className="text-xs text-gray-600">
                                                                {hotspot.organisationunitname} Region
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="font-semibold text-sm">
                                                            {(() => {
                                                                const casesKey = Object.keys(hotspot || {}).find(key => key.includes('cases'));
                                                                const casesValue = casesKey && hotspot[casesKey] !== null && hotspot[casesKey] !== undefined 
                                                                    ? hotspot[casesKey] 
                                                                    : 0;
                                                                return casesValue.toLocaleString();
                                                            })()}
                                                        </p>
                                                        <p className="text-xs text-gray-600 capitalize">{hotspot.severity}</p>
                                                    </div>
                                                </div>
                                            ))
                                    )}
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
