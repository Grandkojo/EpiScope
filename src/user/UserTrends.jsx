// "use client"

// import { useState, useEffect } from "react"
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
// import { Button } from "../components/ui/button"
// import  Badge  from "../components/ui/badge"
// import { ChartContainer, ChartTooltip, ChartTooltipContent } from "../components/ui/chart"
// import {
//   LineChart,
//   Line,
//   AreaChart,
//   Area,
//   BarChart,
//   Bar,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   ResponsiveContainer,
//   PieChart,
//   Pie,
//   Cell,
// } from "recharts"
// import {
//   TrendingUp,
//   TrendingDown,
//   Users,
//   Activity,
//   AlertTriangle,
//   MapPin,
//   Filter,
//   Download,
//   RefreshCw,
//   Eye,
//   Heart,
//   Clock,
//   Globe,
//   Shield,
//   BarChart3,
//   PieChartIcon,
//   LineChartIcon,
// } from "lucide-react"

// // Dummy data for trends
// const weeklyTrends = [
//   { day: "Mon", cases: 1200, recovered: 980, deaths: 45, active: 175 },
//   { day: "Tue", cases: 1350, recovered: 1100, deaths: 52, active: 198 },
//   { day: "Wed", cases: 1180, recovered: 950, deaths: 38, active: 192 },
//   { day: "Thu", cases: 1420, recovered: 1150, deaths: 48, active: 222 },
//   { day: "Fri", cases: 1380, recovered: 1120, deaths: 41, active: 219 },
//   { day: "Sat", cases: 1500, recovered: 1200, deaths: 55, active: 245 },
//   { day: "Sun", cases: 1280, recovered: 1050, deaths: 42, active: 188 },
// ]

// const monthlyComparison = [
//   { month: "Jan", diabetes: 1200, malaria: 2800, cholera: 450, tuberculosis: 680 },
//   { month: "Feb", diabetes: 1350, malaria: 3200, cholera: 520, tuberculosis: 720 },
//   { month: "Mar", diabetes: 1180, malaria: 2900, cholera: 380, tuberculosis: 650 },
//   { month: "Apr", diabetes: 1420, malaria: 3400, cholera: 620, tuberculosis: 780 },
//   { month: "May", diabetes: 1380, malaria: 3100, cholera: 580, tuberculosis: 740 },
//   { month: "Jun", diabetes: 1500, malaria: 3600, cholera: 680, tuberculosis: 820 },
// ]

// const ageGroupData = [
//   { name: "0-18", value: 15, color: "#3b82f6" },
//   { name: "19-35", value: 35, color: "#10b981" },
//   { name: "36-50", value: 28, color: "#f59e0b" },
//   { name: "51-65", value: 18, color: "#ef4444" },
//   { name: "65+", value: 4, color: "#8b5cf6" },
// ]

// const hotspotData = [
//   { region: "North America", cases: 15420, trend: "up", change: 12.5, severity: "high" },
//   { region: "Europe", cases: 12800, trend: "down", change: -8.2, severity: "medium" },
//   { region: "Asia", cases: 28900, trend: "up", change: 15.8, severity: "high" },
//   { region: "Africa", cases: 8600, trend: "up", change: 22.1, severity: "critical" },
//   { region: "South America", cases: 6400, trend: "down", change: -5.4, severity: "low" },
//   { region: "Oceania", cases: 1200, trend: "stable", change: 0.8, severity: "low" },
// ]

// const recentAlerts = [
//   {
//     id: 1,
//     type: "outbreak",
//     message: "New malaria outbreak detected in Region A",
//     time: "2 hours ago",
//     severity: "high",
//   },
//   {
//     id: 2,
//     type: "trend",
//     message: "Diabetes cases trending upward in urban areas",
//     time: "4 hours ago",
//     severity: "medium",
//   },
//   { id: 3, type: "recovery", message: "Recovery rate improved by 15% this week", time: "6 hours ago", severity: "low" },
//   {
//     id: 4,
//     type: "critical",
//     message: "Critical threshold reached in Region C",
//     time: "8 hours ago",
//     severity: "critical",
//   },
// ]

// const chartConfig = {
//   cases: { label: "Cases", color: "hsl(var(--chart-1))" },
//   recovered: { label: "Recovered", color: "hsl(var(--chart-2))" },
//   deaths: { label: "Deaths", color: "hsl(var(--chart-3))" },
//   active: { label: "Active", color: "hsl(var(--chart-4))" },
//   diabetes: { label: "Diabetes", color: "#3b82f6" },
//   malaria: { label: "Malaria", color: "#10b981" },
//   cholera: { label: "Cholera", color: "#f59e0b" },
//   tuberculosis: { label: "Tuberculosis", color: "#ef4444" },
// }

// // Animated counter component
// function AnimatedCounter({ end, duration = 2000, suffix = "" }) {
//   const [count, setCount] = useState(0)

//   useEffect(() => {
//     let startTime
//     const animate = (currentTime) => {
//       if (!startTime) startTime = currentTime
//       const progress = Math.min((currentTime - startTime) / duration, 1)
//       setCount(Math.floor(progress * end))
//       if (progress < 1) {
//         requestAnimationFrame(animate)
//       }
//     }
//     requestAnimationFrame(animate)
//   }, [end, duration])

//   return (
//     <span>
//       {count.toLocaleString()}
//       {suffix}
//     </span>
//   )
// }

// // Trend indicator component
// function TrendIndicator({ trend, change }) {
//   const isPositive = trend === "up"
//   const isNegative = trend === "down"

//   return (
//     <div
//       className={`flex items-center gap-1 text-sm ${isPositive ? "text-red-600" : isNegative ? "text-green-600" : "text-gray-600"
//         }`}
//     >
//       {isPositive && <TrendingUp className="h-4 w-4" />}
//       {isNegative && <TrendingDown className="h-4 w-4" />}
//       {trend === "stable" && <Activity className="h-4 w-4" />}
//       <span>{Math.abs(change)}%</span>
//     </div>
//   )
// }

// // Severity badge component
// function SeverityBadge({ severity }) {
//   const colors = {
//     low: "bg-green-100 text-green-800 border-green-200",
//     medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
//     high: "bg-orange-100 text-orange-800 border-orange-200",
//     critical: "bg-red-100 text-red-800 border-red-200",
//   }

//   return (
//     <Badge variant="outline" className={colors[severity]}>
//       {severity.charAt(0).toUpperCase() + severity.slice(1)}
//     </Badge>
//   )
// }

// export default function UserTrends() {
//   const [selectedTimeframe, setSelectedTimeframe] = useState("week")
//   const [selectedChart, setSelectedChart] = useState("line")
//   const [isRefreshing, setIsRefreshing] = useState(false)

//   const handleRefresh = () => {
//     setIsRefreshing(true)
//     setTimeout(() => setIsRefreshing(false), 1500)
//   }

//   const handleExport = () => {
//     console.log("Exporting data...")
//     // Add export functionality here
//   }

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
//       <div className="max-w-7xl mx-auto space-y-6">
//         {/* Header */}
//         <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
//           <div>
//             <h1 className="text-3xl font-bold text-gray-900 mb-2">Epidemic Trends Dashboard</h1>
//             <p className="text-gray-600">Real-time monitoring and analysis of disease patterns</p>
//           </div>

//           <div className="flex items-center gap-3">
//             <Button
//               variant="outline"
//               size="sm"
//               onClick={handleRefresh}
//               disabled={isRefreshing}
//               className="flex items-center gap-2 bg-transparent"
//             >
//               <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
//               Refresh
//             </Button>
//             <Button
//               variant="outline"
//               size="sm"
//               onClick={handleExport}
//               className="flex items-center gap-2 bg-transparent"
//             >
//               <Download className="h-4 w-4" />
//               Export
//             </Button>
//             <Button size="sm" className="flex items-center gap-2">
//               <Filter className="h-4 w-4" />
//               Filters
//             </Button>
//           </div>
//         </div>

//         {/* Key Metrics */}
//         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
//           {[
//             {
//               title: "Total Cases",
//               value: 73250,
//               change: 12.5,
//               trend: "up",
//               icon: Users,
//               color: "text-blue-600",
//               bgColor: "bg-blue-50",
//             },
//             {
//               title: "Active Cases",
//               value: 8420,
//               change: -5.2,
//               trend: "down",
//               icon: Activity,
//               color: "text-orange-600",
//               bgColor: "bg-orange-50",
//             },
//             {
//               title: "Recovered",
//               value: 64180,
//               change: 8.7,
//               trend: "up",
//               icon: Heart,
//               color: "text-green-600",
//               bgColor: "bg-green-50",
//             },
//             {
//               title: "Critical Areas",
//               value: 15,
//               change: 25.0,
//               trend: "up",
//               icon: AlertTriangle,
//               color: "text-red-600",
//               bgColor: "bg-red-50",
//             },
//           ].map((metric, index) => (
//             <Card
//               key={index}
//               className="bg-white/80 backdrop-blur-sm border-blue-100 hover:shadow-lg transition-all duration-300"
//             >
//               <CardContent className="p-6">
//                 <div className="flex items-center justify-between mt-auto pt-2">
//                   <div>
//                     <p className="text-sm font-medium text-gray-600 mb-1">{metric.title}</p>
//                     <p className="text-2xl font-bold text-gray-900">
//                       <AnimatedCounter end={metric.value} />
//                     </p>
//                   </div>
//                   <div className={`p-3 rounded-full ${metric.bgColor}`}>
//                     <metric.icon className={`h-6 w-6 ${metric.color}`} />
//                   </div>
//                 </div>
//                 <div className="mt-4 flex items-center justify-between">
//                   <TrendIndicator trend={metric.trend} change={metric.change} />
//                   <span className="text-xs text-gray-500">vs last week</span>
//                 </div>
//               </CardContent>
//             </Card>
//           ))}
//         </div>

//         {/* Charts Section */}
//         <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
//           {/* Weekly Trends */}
//           <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
//             <CardHeader className="pb-4">
//               <div className="flex items-center justify-between">
//                 <div>
//                   <CardTitle className="flex items-center gap-2">
//                     <LineChartIcon className="h-5 w-5 text-blue-600" />
//                     Weekly Trends
//                   </CardTitle>
//                   <CardDescription>Cases progression over the last 7 days</CardDescription>
//                 </div>
//                 <div className="flex items-center gap-2">
//                   <Button
//                     variant={selectedChart === "line" ? "default" : "outline"}
//                     size="sm"
//                     onClick={() => setSelectedChart("line")}
//                   >
//                     <LineChartIcon className="h-4 w-4" />
//                   </Button>
//                   <Button
//                     variant={selectedChart === "area" ? "default" : "outline"}
//                     size="sm"
//                     onClick={() => setSelectedChart("area")}
//                   >
//                     <BarChart3 className="h-4 w-4" />
//                   </Button>
//                 </div>
//               </div>
//             </CardHeader>
//             <CardContent>
//               <ChartContainer config={chartConfig} className="h-[300px] w-full">
//                 <ResponsiveContainer width="100%" height="100%">
//                   {selectedChart === "line" ? (
//                     <LineChart data={weeklyTrends}>
//                       <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
//                       <XAxis dataKey="day" tick={{ fontSize: 12 }} />
//                       <YAxis tick={{ fontSize: 12 }} />
//                       <ChartTooltip content={<ChartTooltipContent />} />
//                       <Line
//                         type="monotone"
//                         dataKey="cases"
//                         stroke="var(--color-cases)"
//                         strokeWidth={3}
//                         dot={{ fill: "var(--color-cases)", strokeWidth: 2, r: 4 }}
//                       />
//                       <Line
//                         type="monotone"
//                         dataKey="recovered"
//                         stroke="var(--color-recovered)"
//                         strokeWidth={2}
//                         dot={{ fill: "var(--color-recovered)", strokeWidth: 2, r: 3 }}
//                       />
//                     </LineChart>
//                   ) : (
//                     <AreaChart data={weeklyTrends}>
//                       <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
//                       <XAxis dataKey="day" tick={{ fontSize: 12 }} />
//                       <YAxis tick={{ fontSize: 12 }} />
//                       <ChartTooltip content={<ChartTooltipContent />} />
//                       <Area
//                         type="monotone"
//                         dataKey="cases"
//                         stackId="1"
//                         stroke="var(--color-cases)"
//                         fill="var(--color-cases)"
//                         fillOpacity={0.6}
//                       />
//                       <Area
//                         type="monotone"
//                         dataKey="recovered"
//                         stackId="1"
//                         stroke="var(--color-recovered)"
//                         fill="var(--color-recovered)"
//                         fillOpacity={0.6}
//                       />
//                     </AreaChart>
//                   )}
//                 </ResponsiveContainer>
//               </ChartContainer>
//             </CardContent>
//           </Card>

//           {/* Disease Comparison */}
//           <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
//             <CardHeader className="pb-4">
//               <CardTitle className="flex items-center gap-2">
//                 <BarChart3 className="h-5 w-5 text-green-600" />
//                 Disease Comparison
//               </CardTitle>
//               <CardDescription>Monthly cases by disease type</CardDescription>
//             </CardHeader>
//             <CardContent>
//               <ChartContainer config={chartConfig} className="h-[300px] w-full">
//                 <ResponsiveContainer width="100%" height="100%">
//                   <BarChart data={monthlyComparison}>
//                     <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
//                     <XAxis dataKey="month" tick={{ fontSize: 12 }} />
//                     <YAxis tick={{ fontSize: 12 }} />
//                     <ChartTooltip content={<ChartTooltipContent />} />
//                     <Bar dataKey="diabetes" fill="var(--color-diabetes)" radius={[2, 2, 0, 0]} />
//                     <Bar dataKey="malaria" fill="var(--color-malaria)" radius={[2, 2, 0, 0]} />
//                     <Bar dataKey="cholera" fill="var(--color-cholera)" radius={[2, 2, 0, 0]} />
//                     <Bar dataKey="tuberculosis" fill="var(--color-tuberculosis)" radius={[2, 2, 0, 0]} />
//                   </BarChart>
//                 </ResponsiveContainer>
//               </ChartContainer>
//             </CardContent>
//           </Card>
//         </div>

//         {/* Age Demographics and Hotspots */}
//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//           {/* Age Demographics */}
//           <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
//             <CardHeader className="pb-4">
//               <CardTitle className="flex items-center gap-2">
//                 <PieChartIcon className="h-5 w-5 text-purple-600" />
//                 Age Demographics
//               </CardTitle>
//               <CardDescription>Cases distribution by age group</CardDescription>
//             </CardHeader>
//             <CardContent>
//               <div className="h-[250px] w-full">
//                 <ResponsiveContainer width="100%" height="100%">
//                   <PieChart>
//                     <Pie
//                       data={ageGroupData}
//                       cx="50%"
//                       cy="50%"
//                       innerRadius={60}
//                       outerRadius={100}
//                       paddingAngle={5}
//                       dataKey="value"
//                     >
//                       {ageGroupData.map((entry, index) => (
//                         <Cell key={`cell-${index}`} fill={entry.color} />
//                       ))}
//                     </Pie>
//                     <ChartTooltip
//                       content={({ active, payload }) => {
//                         if (active && payload && payload.length) {
//                           return (
//                             <div className="bg-white p-3 border rounded-lg shadow-lg">
//                               <p className="font-medium">{payload[0].payload.name}</p>
//                               <p className="text-sm text-gray-600">{payload[0].value}% of cases</p>
//                             </div>
//                           )
//                         }
//                         return null
//                       }}
//                     />
//                   </PieChart>
//                 </ResponsiveContainer>
//               </div>
//               <div className="mt-4 space-y-2">
//                 {ageGroupData.map((item, index) => (
//                   <div key={index} className="flex items-center justify-between">
//                     <div className="flex items-center gap-2">
//                       <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
//                       <span className="text-sm font-medium">{item.name}</span>
//                     </div>
//                     <span className="text-sm text-gray-600">{item.value}%</span>
//                   </div>
//                 ))}
//               </div>
//             </CardContent>
//           </Card>

//           {/* Global Hotspots */}
//           <Card className="lg:col-span-2 bg-white/80 backdrop-blur-sm border-blue-100">
//             <CardHeader className="pb-4">
//               <CardTitle className="flex items-center gap-2">
//                 <MapPin className="h-5 w-5 text-red-600" />
//                 Global Hotspots
//               </CardTitle>
//               <CardDescription>Regional outbreak monitoring and severity levels</CardDescription>
//             </CardHeader>
//             <CardContent>
//               <div className="space-y-4">
//                 {hotspotData.map((hotspot, index) => (
//                   <div
//                     key={index}
//                     className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
//                   >
//                     <div className="flex items-center gap-4">
//                       <div className="flex items-center gap-2">
//                         <Globe className="h-5 w-5 text-gray-600" />
//                         <div>
//                           <p className="font-medium text-gray-900">{hotspot.region}</p>
//                           <p className="text-sm text-gray-600">{hotspot.cases.toLocaleString()} cases</p>
//                         </div>
//                       </div>
//                     </div>
//                     <div className="flex items-center gap-4">
//                       <TrendIndicator trend={hotspot.trend} change={hotspot.change} />
//                       <SeverityBadge severity={hotspot.severity} />
//                       <Button variant="ghost" size="sm">
//                         <Eye className="h-4 w-4" />
//                       </Button>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             </CardContent>
//           </Card>
//         </div>

//         {/* Recent Alerts */}
//         <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
//           <CardHeader className="pb-4">
//             <CardTitle className="flex items-center gap-2">
//               <AlertTriangle className="h-5 w-5 text-orange-600" />
//               Recent Alerts
//             </CardTitle>
//             <CardDescription>Latest notifications and system updates</CardDescription>
//           </CardHeader>
//           <CardContent>
//             <div className="space-y-4">
//               {recentAlerts.map((alert) => (
//                 <div
//                   key={alert.id}
//                   className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
//                 >
//                   <div
//                     className={`p-2 rounded-full ${alert.severity === "critical"
//                         ? "bg-red-100"
//                         : alert.severity === "high"
//                           ? "bg-orange-100"
//                           : alert.severity === "medium"
//                             ? "bg-yellow-100"
//                             : "bg-green-100"
//                       }`}
//                   >
//                     {alert.type === "outbreak" && <AlertTriangle className="h-4 w-4 text-red-600" />}
//                     {alert.type === "trend" && <TrendingUp className="h-4 w-4 text-orange-600" />}
//                     {alert.type === "recovery" && <Heart className="h-4 w-4 text-green-600" />}
//                     {alert.type === "critical" && <Shield className="h-4 w-4 text-red-600" />}
//                   </div>
//                   <div className="flex-1">
//                     <p className="font-medium text-gray-900">{alert.message}</p>
//                     <div className="flex items-center gap-2 mt-1">
//                       <Clock className="h-3 w-3 text-gray-400" />
//                       <span className="text-xs text-gray-500">{alert.time}</span>
//                       <SeverityBadge severity={alert.severity} />
//                     </div>
//                   </div>
//                   <Button variant="ghost" size="sm">
//                     <Eye className="h-4 w-4" />
//                   </Button>
//                 </div>
//               ))}
//             </div>
//           </CardContent>
//         </Card>
//       </div>
//     </div>
//   )
// }


"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import  Badge  from "../components/ui/Badge"
import {
  TrendingUp,
  Activity,
  AlertTriangle,
  Filter,
  RefreshCw,
  Eye,
  Heart,
  Clock,
  Shield,
  LineChartIcon,
  BookOpen,
  Calendar,
  User,
  MessageCircle,
  Share2,
  Bookmark,
  Search,
  Tag,
  ThumbsUp,
  FileText,
  Stethoscope,
  Brain,
} from "lucide-react"

// Dummy data for weekly trends (keeping original)
const weeklyTrends = [
  { day: "Mon", cases: 1200, recovered: 980, deaths: 45, active: 175 },
  { day: "Tue", cases: 1350, recovered: 1100, deaths: 52, active: 198 },
  { day: "Wed", cases: 1180, recovered: 950, deaths: 38, active: 192 },
  { day: "Thu", cases: 1420, recovered: 1150, deaths: 48, active: 222 },
  { day: "Fri", cases: 1380, recovered: 1120, deaths: 41, active: 219 },
  { day: "Sat", cases: 1500, recovered: 1200, deaths: 55, active: 245 },
  { day: "Sun", cases: 1280, recovered: 1050, deaths: 42, active: 188 },
]

// Recent alerts (keeping original)
const recentAlerts = [
  {
    id: 1,
    type: "outbreak",
    message: "New malaria outbreak detected in Region A",
    time: "2 hours ago",
    severity: "high",
  },
  {
    id: 2,
    type: "trend",
    message: "Diabetes cases trending upward in urban areas",
    time: "4 hours ago",
    severity: "medium",
  },
  { id: 3, type: "recovery", message: "Recovery rate improved by 15% this week", time: "6 hours ago", severity: "low" },
  {
    id: 4,
    type: "critical",
    message: "Critical threshold reached in Region C",
    time: "8 hours ago",
    severity: "critical",
  },
]

// New health blog data
const featuredArticles = [
  {
    id: 1,
    title: "Understanding the Latest Breakthrough in Malaria Prevention",
    excerpt: "Scientists have developed a new vaccine that shows 95% efficacy in preventing malaria infections...",
    author: "Dr. Sarah Johnson",
    publishDate: "2024-01-15",
    readTime: "8 min read",
    category: "Research",
    image: "/placeholder.svg?height=200&width=300",
    likes: 245,
    comments: 18,
    featured: true,
  },
  {
    id: 2,
    title: "Mental Health in the Digital Age: Challenges and Solutions",
    excerpt: "Exploring how technology impacts mental health and practical strategies for maintaining wellbeing...",
    author: "Dr. Michael Chen",
    publishDate: "2024-01-14",
    readTime: "6 min read",
    category: "Mental Health",
    image: "/placeholder.svg?height=200&width=300",
    likes: 189,
    comments: 24,
    featured: true,
  },
  {
    id: 3,
    title: "Nutrition Guidelines for Diabetes Management",
    excerpt: "Evidence-based dietary recommendations for effective diabetes control and prevention...",
    author: "Dr. Emily Rodriguez",
    publishDate: "2024-01-13",
    readTime: "10 min read",
    category: "Diabetes",
    image: "/placeholder.svg?height=200&width=300",
    likes: 156,
    comments: 12,
    featured: false,
  },
]

const recentArticles = [
  {
    id: 4,
    title: "The Role of Exercise in Cardiovascular Health",
    excerpt: "How regular physical activity can significantly reduce heart disease risk...",
    author: "Dr. James Wilson",
    publishDate: "2024-01-12",
    readTime: "7 min read",
    category: "Malaria",
    likes: 134,
    comments: 9,
  },
  {
    id: 5,
    title: "Antibiotic Resistance: A Growing Global Concern",
    excerpt: "Understanding the causes and consequences of antibiotic resistance...",
    author: "Dr. Lisa Park",
    publishDate: "2024-01-11",
    readTime: "9 min read",
    category: "Infectious Disease",
    likes: 198,
    comments: 15,
  },
  {
    id: 6,
    title: "Sleep Hygiene: Essential Tips for Better Rest",
    excerpt: "Science-backed strategies for improving sleep quality and duration...",
    author: "Dr. Robert Kim",
    publishDate: "2024-01-10",
    readTime: "5 min read",
    // category: "Sleep Medicine",
    likes: 167,
    comments: 21,
  },
]

const categories = [
  { name: "All", count: 156, active: true },
  { name: "Research", count: 34, active: false },
  { name: "Mental Health", count: 28, active: false },
  { name: "Nutrition", count: 22, active: false },
  { name: "Cardiology", count: 19, active: false },
  { name: "Infectious Disease", count: 25, active: false },
  { name: "Sleep Medicine", count: 15, active: false },
]

const blogStats = [
  {
    title: "Total Articles",
    value: 156,
    icon: FileText,
    color: "text-blue-600",
    bgColor: "bg-blue-50",
  },
  {
    title: "Expert Authors",
    value: 24,
    icon: Stethoscope,
    color: "text-green-600",
    bgColor: "bg-green-50",
  },
  {
    title: "Monthly Readers",
    value: 45200,
    icon: Eye,
    color: "text-purple-600",
    bgColor: "bg-purple-50",
  },
  {
    title: "Health Topics",
    value: 12,
    icon: Brain,
    color: "text-orange-600",
    bgColor: "bg-orange-50",
  },
]

const chartConfig = {
  cases: { label: "Cases", color: "hsl(var(--chart-1))" },
  recovered: { label: "Recovered", color: "hsl(var(--chart-2))" },
  deaths: { label: "Deaths", color: "hsl(var(--chart-3))" },
  active: { label: "Active", color: "hsl(var(--chart-4))" },
}

// Animated counter component
function AnimatedCounter({ end, duration = 2000, suffix = "" }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTime
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      setCount(Math.floor(progress * end))
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    requestAnimationFrame(animate)
  }, [end, duration])

  return (
    <span>
      {count.toLocaleString()}
      {suffix}
    </span>
  )
}

// Severity badge component
function SeverityBadge({ severity }) {
  const colors = {
    low: "bg-green-100 text-green-800 border-green-200",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
    high: "bg-orange-100 text-orange-800 border-orange-200",
    critical: "bg-red-100 text-red-800 border-red-200",
  }

  return (
    <Badge variant="outline" className={colors[severity]}>
      {severity.charAt(0).toUpperCase() + severity.slice(1)}
    </Badge>
  )
}

// Article card component
function ArticleCard({ article }) {
  return (
    <Card className="bg-white/80 backdrop-blur-sm border-blue-100 hover:shadow-lg transition-all duration-300 h-full flex flex-col">
      <div>
        <div>
          <div className="aspect-video bg-gradient-to-br from-blue-100 to-green-100 rounded-t-lg flex items-center justify-center">
            <BookOpen className="h-12 w-12 text-blue-600" />
          </div>
        </div>
        <div className="flex flex-col flex-1 p-6">
          <div className="flex items-center gap-2 mb-4">
          <Badge variant="secondary" className="bg-blue-100 text-blue-800">
          {article.category}
          </Badge>
          {article.featured && (
          <Badge className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white">Featured</Badge>
          )}
          </div>
          
          <h3 className="font-bold text-gray-900 mb-4 text-lg">{article.title}</h3>
          
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">{article.excerpt}</p>
          
          <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
          <div className="flex items-center gap-2">
          <User className="h-4 w-4" />
          {article.author}
          </div>
          <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          {new Date(article.publishDate).toLocaleDateString()}
          </div>
          <div className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          {article.readTime}
          </div>
          </div>
          
          <div className="flex items-center justify-between mt-auto pt-2">
          <div className="flex items-center gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-2">
          <ThumbsUp className="h-4 w-4" />
          {article.likes}
          </div>
          <div className="flex items-center gap-2">
          <MessageCircle className="h-4 w-4" />
          {article.comments}
          </div>
          </div>
          
          <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
          <Bookmark className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
          <Share2 className="h-4 w-4" />
          </Button>
          <Button size="sm" className="px-4 py-2">Read More</Button>
          </div>
          </div>
        </div>
      </div>
    </Card>
  )
}

export default function HealthBlog() {
  const [selectedChart, setSelectedChart] = useState("line")
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState("All")

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 1500)
  }

  const handleExport = () => {
    console.log("Exporting data...")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Health Blog & Articles</h1>
            <p className="text-gray-600">Expert insights and latest research in healthcare</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search articles..."
                className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center gap-2 bg-transparent"
            >
              <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button size="sm" className="flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Filters
            </Button>
          </div>
        </div>

        {/* Blog Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {blogStats.map((stat, index) => (
            <Card
              key={index}
              className="bg-white/80 backdrop-blur-sm border-blue-100 hover:shadow-lg transition-all duration-300"
            >
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900">
                      <AnimatedCounter end={stat.value} />
                    </p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.bgColor}`}>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Categories */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
          <CardContent className="p-6">
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Button
                  key={category.name}
                  variant={category.name === selectedCategory ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category.name)}
                  className="flex items-center gap-2"
                >
                  <Tag className="h-3 w-3" />
                  {category.name}
                  <Badge variant="secondary" className="ml-1 text-xs">
                    {category.count}
                  </Badge>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card> 

        {/* Recent Alerts */}
        <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Health Alerts
            </CardTitle>
            <CardDescription>Latest health notifications and updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div
                    className={`p-2 rounded-full ${
                      alert.severity === "critical"
                        ? "bg-red-100"
                        : alert.severity === "high"
                          ? "bg-orange-100"
                          : alert.severity === "medium"
                            ? "bg-yellow-100"
                            : "bg-green-100"
                    }`}
                  >
                    {alert.type === "outbreak" && <AlertTriangle className="h-4 w-4 text-red-600" />}
                    {alert.type === "trend" && <TrendingUp className="h-4 w-4 text-orange-600" />}
                    {alert.type === "recovery" && <Heart className="h-4 w-4 text-green-600" />}
                    {alert.type === "critical" && <Shield className="h-4 w-4 text-red-600" />}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{alert.message}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Clock className="h-3 w-3 text-gray-400" />
                      <span className="text-xs text-gray-500">{alert.time}</span>
                      <SeverityBadge severity={alert.severity} />
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Featured Articles */}
         <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Featured Articles</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {featuredArticles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        </div> 

        {/* Charts Section - Weekly Trends */}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <LineChartIcon className="h-5 w-5 text-blue-600" />
                    Weekly Health Trends
                  </CardTitle>
                  <CardDescription>Health metrics progression over the last 7 days</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant={selectedChart === "line" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedChart("line")}
                  >
                    <LineChartIcon className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={selectedChart === "area" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedChart("area")}
                  >
                    <Activity className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  {selectedChart === "line" ? (
                    <LineChart data={weeklyTrends}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line
                        type="monotone"
                        dataKey="cases"
                        stroke="var(--color-cases)"
                        strokeWidth={3}
                        dot={{ fill: "var(--color-cases)", strokeWidth: 2, r: 4 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="recovered"
                        stroke="var(--color-recovered)"
                        strokeWidth={2}
                        dot={{ fill: "var(--color-recovered)", strokeWidth: 2, r: 3 }}
                      />
                    </LineChart>
                  ) : (
                    <AreaChart data={weeklyTrends}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Area
                        type="monotone"
                        dataKey="cases"
                        stackId="1"
                        stroke="var(--color-cases)"
                        fill="var(--color-cases)"
                        fillOpacity={0.6}
                      />
                      <Area
                        type="monotone"
                        dataKey="recovered"
                        stackId="1"
                        stroke="var(--color-recovered)"
                        fill="var(--color-recovered)"
                        fillOpacity={0.6}
                      />
                    </AreaChart>
                  )}
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card> */}

          {/* Recent Articles List */}
           {/* <Card className="bg-white/80 backdrop-blur-sm border-blue-100">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-green-600" />
                Recent Articles
              </CardTitle>
              <CardDescription>Latest health articles and research</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentArticles.slice(0, 4).map((article) => (
                  <div
                    key={article.id}
                    className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                  >
                    <div className="p-2 bg-blue-100 rounded-full">
                      <FileText className="h-4 w-4 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 text-sm mb-1">{article.title}</h4>
                      <p className="text-sm text-gray-600 mb-2 line-clamp-2">{article.excerpt}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>{article.author}</span>
                        <span>{article.readTime}</span>
                        <div className="flex items-center gap-1">
                          <ThumbsUp className="h-3 w-3" />
                          {article.likes}
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 text-xs">
                      {article.category}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>  */}
        </div>

      </div>
    </div>
  )
}
