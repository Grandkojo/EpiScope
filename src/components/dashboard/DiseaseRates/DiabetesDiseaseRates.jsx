import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { useEffect, useState } from "react"

export const DiabetesDiseaseRates = ({ dashboardDataRegionRates, isDashboardDataRegionRatesLoading, isDashboardDataRegionRatesError, selectedDisease, selectedDiseaseYear }) => {
    const [animatedData, setAnimatedData] = useState([])
    const [isAnimating, setIsAnimating] = useState(false)

    useEffect(() => {
        if (dashboardDataRegionRates && dashboardDataRegionRates.length > 0) {
            // Filter out regions with 0 cases
            const filteredData = dashboardDataRegionRates.filter(item => item.cases > 0)
            
            if (filteredData.length === 0) {
                setAnimatedData([])
                return
            }

            setIsAnimating(true)
            // Start with zero values for animation
            const initialData = filteredData.map(item => ({
                ...item,
                animatedRate: 0
            }))
            setAnimatedData(initialData)

            // Animate each bar with staggered delay
            const animationPromises = filteredData.map((item, index) => {
                return new Promise(resolve => {
                    setTimeout(() => {
                        setAnimatedData(prev => 
                            prev.map((dataItem, dataIndex) => 
                                dataIndex === index 
                                    ? { ...dataItem, animatedRate: item.rate }
                                    : dataItem
                            )
                        )
                        resolve()
                    }, index * 150) // 150ms delay between each bar
                })
            })

            Promise.all(animationPromises).then(() => {
                setTimeout(() => setIsAnimating(false), 500)
            })
        } else {
            setAnimatedData([])
        }
    }, [dashboardDataRegionRates])

    if (isDashboardDataRegionRatesLoading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <BarChart className="h-5 w-5 text-health-400" />
                        <span>Regional Disease Rates (per 1000 population) - {selectedDisease} - {selectedDiseaseYear}</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center h-[400px]">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-health-400"></div>
                    </div>
                </CardContent>
            </Card>
        )
    }

    if (isDashboardDataRegionRatesError) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <BarChart className="h-5 w-5 text-health-400" />
                        <span>Regional Disease Rates (per 1000 population) - {selectedDisease} - {selectedDiseaseYear}</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center h-[400px] text-red-500">
                        Error loading data. Please try again.
                    </div>
                </CardContent>
            </Card>
        )
    }

    // If no data or all regions have 0 cases
    if (!animatedData || animatedData.length === 0) {
        return (
            <Card className="transition-all duration-300 hover:shadow-lg">
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <BarChart className="h-5 w-5 text-health-400" />
                        <span>Regional Disease Rates (per 1000 population) - {selectedDisease} - {selectedDiseaseYear}</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center h-[400px] text-gray-500">
                        No cases reported in any region for this period.
                    </div>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card className="transition-all duration-300 hover:shadow-lg">
            <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                    <BarChart className="h-5 w-5 text-health-400" />
                    <span>Regional Disease Rates (per 1000 population) - {selectedDisease} - {selectedDiseaseYear}</span>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                        data={animatedData}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                        <XAxis 
                            dataKey="region" 
                            stroke="#9ca3af" 
                            angle={-45} 
                            textAnchor="end" 
                            height={100}
                            tick={{ fontSize: 12 }}
                        />
                        <YAxis 
                            stroke="#9ca3af" 
                            tick={{ fontSize: 12 }}
                            label={{ value: 'Rate per 1000', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9ca3af' } }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#1f2937",
                                border: "1px solid #374151",
                                borderRadius: "8px",
                                color: "#f9fafb"
                            }}
                            formatter={(value, name) => [
                                `${value.toFixed(2)} per 1000`, 
                                name
                            ]}
                            labelFormatter={(label) => `Region: ${label}`}
                        />
                        <Legend />
                        <Bar 
                            dataKey="animatedRate" 
                            fill="#22c55e" 
                            name={`${selectedDisease} Rate`}
                            radius={[4, 4, 0, 0]}
                            className="transition-all duration-500 ease-out"
                        />
                    </BarChart>
                </ResponsiveContainer>
                
                {/* Summary stats */}
                {!isAnimating && animatedData.length > 0 && (
                    <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                        <div className="text-center p-2 bg-gray-800 rounded-lg">
                            <div className="text-gray-200 font-semibold">
                                {animatedData.length}
                            </div>
                            <div className="text-gray-400">Regions with Cases</div>
                        </div>
                        <div className="text-center p-2 bg-gray-800 rounded-lg">
                            <div className="text-gray-200 font-semibold">
                                {animatedData.reduce((sum, item) => sum + item.cases, 0).toLocaleString()}
                            </div>
                            <div className="text-gray-400">Total Cases</div>
                        </div>
                        <div className="text-center p-2 bg-gray-800 rounded-lg">
                            <div className="text-gray-200 font-semibold">
                                {(animatedData.reduce((sum, item) => sum + item.rate, 0) / animatedData.length).toFixed(2)}
                            </div>
                            <div className="text-gray-400">Avg Rate</div>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}