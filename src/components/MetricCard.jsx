import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

const MetricCard = ({ title, value, change, icon: Icon, trend, color = "health" }) => {
  const getTrendIcon = () => {
    if (trend === "up") return <TrendingUp className="h-4 w-4 text-green-500" />
    if (trend === "down") return <TrendingDown className="h-4 w-4 text-red-500" />
    return <Minus className="h-4 w-4 text-gray-500" />
  }

  const getColorClasses = () => {
    switch (color) {
      case "danger":
        return "text-red-500 bg-red-100 border-red-200"
      case "warning":
        return "text-yellow-500 bg-yellow-100 border-yellow-200"
      case "info":
        return "text-blue-500 bg-blue-100 border-blue-200"
      default:
        return "text-green-600 bg-green-100 border-green-200"
    }
  }

  return (
    <Card className="transition-all duration-200 hover:shadow-lg hover:scale-105">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
        <div className={`p-2 rounded-lg ${getColorClasses()}`}>
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        {change && (
          <div className="flex items-center space-x-1 text-xs text-gray-500 mt-1">
            {getTrendIcon()}
            <span>{change}% from last month</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default MetricCard
