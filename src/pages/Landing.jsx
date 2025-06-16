"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "../components/ui/chart"
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts"
import {
  Activity,
  Shield,
  TrendingUp,
  Users,
  AlertTriangle,
  Heart,
  Zap,
  Microscope,
  Stethoscope,
  Pill,
} from "lucide-react"

// Animated background component
function AnimatedBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Floating particles */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-blue-400/20 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 2}s`,
            }}
          />
        ))}
      </div>

      {/* Animated grid */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 to-green-50/30">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `
            linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px)
          `,
            backgroundSize: "50px 50px",
            animation: "grid-move 20s linear infinite",
          }}
        />
      </div>

      {/* Floating medical icons */}
      <div className="absolute inset-0">
        {[Heart, Activity, Shield, Microscope, Stethoscope, Pill].map((Icon, i) => (
          <Icon
            key={i}
            className="absolute text-blue-300/20 animate-float"
            size={24}
            style={{
              left: `${10 + i * 15}%`,
              top: `${10 + i * 15}%`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: "3s",
            }}
          />
        ))}
      </div>
    </div>
  )
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

// Scroll animation component
function ScrollReveal({ children, className, delay = 0 }) {
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.unobserve(entry.target)
        }
      },
      {
        threshold: 0.1,
      },
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [])

  return (
    <div
      ref={ref}
      className={`${className} transition-all duration-1000 ${
        isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
      }`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  )
}

// Heartbeat animation component
function HeartbeatIcon({ className }) {
  return (
    <div className={`${className} animate-heartbeat`}>
      <Heart className="text-green-500 w-full h-full" />
    </div>
  )
}

// Pulse wave animation
function PulseWave() {
  return (
    <div className="relative h-20 w-full overflow-hidden my-8">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="h-0.5 w-full bg-gray-250 relative">
          <div className="absolute inset-0">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="absolute h-8 w-8 rounded-full bg-blue-500/30 animate-pulse-wave"
                style={{
                  left: `${20 * i}%`,
                  animationDelay: `${i * 0.2}s`,
                }}
              />
            ))}
          </div>
          <div className="absolute top-1/2 left-0 w-full h-px bg-blue-300/30 transform -translate-y-1/2">
            <svg height="100%" width="100%" className="absolute">
              <path
                d="M0,10 L30,10 L40,0 L50,20 L60,10 L70,10 L80,0 L90,20 L100,10 L110,10"
                fill="none"
                stroke="rgba(59, 130, 246, 0.8)"
                strokeWidth="5"
                className="animate-pulse-line"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Landing() {
  const [activeChart, setActiveChart] = useState("diabetes")

  // Dummy data for different diseases
  const diabetesData = [
    { month: "Jan", cases: 1200, deaths: 45, recovered: 1100 },
    { month: "Feb", cases: 1350, deaths: 52, recovered: 1250 },
    { month: "Mar", cases: 1180, deaths: 38, recovered: 1120 },
    { month: "Apr", cases: 1420, deaths: 48, recovered: 1340 },
    { month: "May", cases: 1380, deaths: 41, recovered: 1310 },
    { month: "Jun", cases: 1500, deaths: 55, recovered: 1420 },
  ]

  const malariaData = [
    { month: "Jan", cases: 2800, deaths: 120, recovered: 2600 },
    { month: "Feb", cases: 3200, deaths: 145, recovered: 2950 },
    { month: "Mar", cases: 2900, deaths: 110, recovered: 2750 },
    { month: "Apr", cases: 3400, deaths: 155, recovered: 3180 },
    { month: "May", cases: 3100, deaths: 135, recovered: 2920 },
    { month: "Jun", cases: 3600, deaths: 168, recovered: 3350 },
  ]

  const choleraData = [
    { month: "Jan", cases: 450, deaths: 25, recovered: 410 },
    { month: "Feb", cases: 520, deaths: 32, recovered: 475 },
    { month: "Mar", cases: 380, deaths: 18, recovered: 355 },
    { month: "Apr", cases: 620, deaths: 38, recovered: 570 },
    { month: "May", cases: 580, deaths: 35, recovered: 530 },
    { month: "Jun", cases: 680, deaths: 42, recovered: 625 },
  ]

  const getCurrentData = () => {
    switch (activeChart) {
      case "malaria":
        return malariaData
      case "cholera":
        return choleraData
      default:
        return diabetesData
    }
  }

  const chartConfig = {
    cases: {
      label: "Cases",
      color: "hsl(var(--chart-1))",
    },
    deaths: {
      label: "Deaths",
      color: "hsl(var(--chart-2))",
    },
    recovered: {
      label: "Recovered",
      color: "hsl(var(--chart-3))",
    },
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-150 relative overflow-hidden">
      <AnimatedBackground />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between p-6 bg-white/80 backdrop-blur-sm border-b border-blue-100">
        <div className="flex items-center space-x-2">
          <Microscope className="h-8 w-8 text-green-600" />
          <span className="text-2xl font-bold text-gray-900">EpiScope</span>
        </div>
        <div className="hidden md:flex items-center space-x-8">
          <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">
            Features
          </a>
          <a href="#analytics" className="text-gray-600 hover:text-blue-600 transition-colors">
            Analytics
          </a>
          <a href="#about" className="text-gray-600 hover:text-blue-600 transition-colors">
            About
          </a>
          <Button variant="outline">Sign In</Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 px-6 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6">
              Advanced Epidemic
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-blue-600 block">
                Monitoring System
              </span>
            </h1>
          </ScrollReveal>

          <ScrollReveal delay={200}>
            <p className="text-xl text-gray-700 mb-8 max-w-2xl mx-auto">
              Real-time tracking and analysis of disease outbreaks with AI-powered insights to protect communities and
              save lives.
            </p>
          </ScrollReveal>

          <ScrollReveal delay={400}>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-green-600 hover:bg-blue-700 text-white px-8 py-4 text-lg">
                Access Dashboard
                <Zap className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="px-8 py-4 text-lg">
                Watch Demo
              </Button>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Animated Health Pulse */}
      <ScrollReveal>
        <div className="relative z-10 px-6">
          <div className="max-w-6xl mx-auto">
            <PulseWave />
          </div>
        </div>
      </ScrollReveal>

      {/* Stats Section */}
      <section className="relative z-10 px-6 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { label: "Active Cases Monitored", value: 125000, icon: Users },
              { label: "Lives Saved", value: 45000, icon: Heart },
              { label: "Countries Covered", value: 89, icon: Shield },
              { label: "Data Points Analyzed", value: 2500000, icon: TrendingUp },
            ].map((stat, index) => (
              <ScrollReveal key={index} delay={index * 100}>
                <Card className="text-center bg-white/80 backdrop-blur-sm border-blue-100 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                  <CardContent className="p-6">
                    <stat.icon className="h-8 w-8 text-green-600 mx-auto mb-4" />
                    <div className="text-3xl font-bold text-gray-900 mb-2">
                      <AnimatedCounter end={stat.value} />
                    </div>
                    <p className="text-gray-600">{stat.label}</p>
                  </CardContent>
                </Card>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Interactive Charts Section */}
      <section id="analytics" className="relative z-10 px-4 sm:px-6 py-20">
        <div className="max-w-7xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">Real-Time Disease Analytics</h2>
              <p className="text-xl text-gray-600">Monitor disease patterns and trends across different regions</p>
            </div>
          </ScrollReveal>

          {/* Chart Toggle Buttons */}
          <ScrollReveal delay={200}>
            <div className="flex justify-center mb-8">
              <div className="bg-white/80 backdrop-blur-sm rounded-lg p-2 border border-blue-100 overflow-x-auto">
                <div className="flex gap-1 min-w-max">
                  {[
                    { key: "diabetes", label: "Diabetes", color: "bg-green-500" },
                    { key: "malaria", label: "Malaria", color: "bg-gray-500" },
                    { key: "cholera", label: "Cholera", color: "bg-green-500" },
                  ].map((disease) => (
                    <button
                      key={disease.key}
                      onClick={() => setActiveChart(disease.key)}
                      className={`px-4 sm:px-6 py-2 rounded-md transition-all duration-300 whitespace-nowrap ${
                        activeChart === disease.key
                          ? `${disease.color} text-white shadow-lg`
                          : "text-gray-600 hover:bg-gray-100"
                      }`}
                    >
                      {disease.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </ScrollReveal>

          {/* Charts Grid - Side by Side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-7xl mx-auto">
            {/* Line Chart */}
            <ScrollReveal delay={300}>
              <Card className="bg-white/80 backdrop-blur-sm border-green-100 h-full min-h-[450px]">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    Cases Trend - {activeChart.charAt(0).toUpperCase() + activeChart.slice(1)}
                  </CardTitle>
                  <CardDescription className="text-sm">Monthly progression over the last 6 months</CardDescription>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <ChartContainer config={chartConfig} className="h-[320px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={getCurrentData()} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="month" tick={{ fontSize: 12 }} axisLine={{ stroke: "#cbd5e1" }} />
                        <YAxis tick={{ fontSize: 12 }} axisLine={{ stroke: "#cbd5e1" }} width={60} />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Line
                          type="monotone"
                          dataKey="cases"
                          stroke="var(--color-cases)"
                          strokeWidth={3}
                          dot={{ fill: "var(--color-cases)", strokeWidth: 2, r: 4 }}
                          activeDot={{ r: 6, stroke: "var(--color-cases)", strokeWidth: 2 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>
            </ScrollReveal>

            {/* Area Chart */}
            <ScrollReveal delay={400}>
              <Card className="bg-white/80 backdrop-blur-sm border-blue-100 h-full min-h-[450px]">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Activity className="h-5 w-5 text-green-600" />
                    Recovery vs Deaths
                  </CardTitle>
                  <CardDescription className="text-sm">Comparative analysis of outcomes</CardDescription>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <ChartContainer config={chartConfig} className="h-[320px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={getCurrentData()} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="month" tick={{ fontSize: 12 }} axisLine={{ stroke: "#cbd5e1" }} />
                        <YAxis tick={{ fontSize: 12 }} axisLine={{ stroke: "#cbd5e1" }} width={60} />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Area
                          type="monotone"
                          dataKey="recovered"
                          stackId="1"
                          stroke="var(--color-recovered)"
                          fill="var(--color-recovered)"
                          fillOpacity={0.6}
                        />
                        <Area
                          type="monotone"
                          dataKey="deaths"
                          stackId="1"
                          stroke="var(--color-deaths)"
                          fill="var(--color-deaths)"
                          fillOpacity={0.6}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* Animated DNA Strand */}
      <ScrollReveal>
        <div className="relative z-10 py-12 overflow-hidden">
          <div className="dna-animation">
            <div className="dna-helix">
              {[...Array(10)].map((_, i) => (
                <div key={i} className="dna-step">
                  <div className="dna-base dna-base-left"></div>
                  <div className="dna-base dna-base-right"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </ScrollReveal>

      {/* Features Section */}
      <section id="features" className="relative z-10 px-6 py-20 bg-white/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">Powerful Features</h2>
              <p className="text-xl text-gray-600">Everything you need for comprehensive epidemic monitoring</p>
            </div>
          </ScrollReveal>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: Activity,
                title: "Real-Time Monitoring",
                description: "Track disease outbreaks as they happen with live data feeds and instant alerts.",
              },
              {
                icon: TrendingUp,
                title: "Predictive Analytics",
                description: "AI-powered forecasting to predict outbreak patterns and potential hotspots.",
              },
              {
                icon: Shield,
                title: "Risk Assessment",
                description: "Comprehensive risk analysis tools to evaluate threat levels and response strategies.",
              },
              {
                icon: Users,
                title: "Population Health",
                description: "Monitor community health metrics and vaccination coverage rates.",
              },
              {
                icon: AlertTriangle,
                title: "Early Warning System",
                description: "Automated alerts for unusual disease patterns and potential outbreaks.",
              },
              {
                icon: Heart,
                title: "Healthcare Integration",
                description: "Seamless integration with healthcare systems and medical databases.",
              },
            ].map((feature, index) => (
              <ScrollReveal key={index} delay={index * 100}>
                <Card className="bg-white/80 backdrop-blur-sm border-blue-100 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                  <CardContent className="p-6 text-center">
                    <feature.icon className="h-12 w-12 text-green-600 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                    <p className="text-gray-600">{feature.description}</p>
                  </CardContent>
                </Card>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Animated Heartbeat Section */}
      <ScrollReveal>
        <div className="relative z-10 py-16 flex justify-center">
          <div className="flex items-center gap-8">
            <HeartbeatIcon className="w-16 h-16" />
            <div className="text-2xl font-bold text-gray-900">Protecting Lives Through Data</div>
            <HeartbeatIcon className="w-16 h-16" />
          </div>
        </div>
      </ScrollReveal>

      {/* CTA Section */}
      <section className="relative z-10 px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <ScrollReveal>
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Ready to Transform Public Health Monitoring?</h2>
          </ScrollReveal>

          <ScrollReveal delay={200}>
            <p className="text-xl text-gray-600 mb-8">
              Join healthcare professionals worldwide who trust EpiScope for epidemic surveillance and response.
            </p>
          </ScrollReveal>

          <ScrollReveal delay={400}>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                className="bg-gradient-to-r from-green-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white px-12 py-4 text-lg shadow-lg hover:shadow-xl transition-all duration-300"
              >
                Launch Dashboard
                <Activity className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="px-12 py-4 text-lg border-blue-200 hover:bg-blue-50">
                Schedule Demo
              </Button>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 bg-gray-900 text-white px-6 py-12">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Microscope className="h-6 w-6 text-green-400" />
                <span className="text-xl font-bold">EpiScope</span>
              </div>
              <p className="text-gray-400">Advanced epidemic monitoring for a healthier world.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Analytics
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    API
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    About
                  </a>
                </li>
                <li>
                  {/* <a href="#" className="hover:text-white transition-colors">
                    Careers
                  </a>
                </li>
                <li> */}
                  <a href="#" className="hover:text-white transition-colors">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Help Center
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Status
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 EpiScope. All rights reserved.</p>
          </div>
        </div>
      </footer>

      <style jsx>{`
        @keyframes grid-move {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-15px); }
        }
        
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        
        @keyframes heartbeat {
          0%, 100% { transform: scale(1); }
          25% { transform: scale(1.1); }
          50% { transform: scale(1); }
          75% { transform: scale(1.2); }
        }
        
        .animate-heartbeat {
          animation: heartbeat 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse-wave {
          0% { transform: scale(0); opacity: 1; }
          100% { transform: scale(3); opacity: 0; }
        }
        
        .animate-pulse-wave {
          animation: pulse-wave 3s ease-out infinite;
        }
        
        @keyframes pulse-line {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .animate-pulse-line {
          animation: pulse-line 3s linear infinite;
        }
        
        /* DNA Animation */
        .dna-animation {
          height: 100px;
          display: flex;
          justify-content: center;
          align-items: center;
          overflow: hidden;
        }
        
        .dna-helix {
          display: flex;
          flex-direction: column;
          animation: dna-rotate 10s linear infinite;
        }
        
        .dna-step {
          display: flex;
          justify-content: center;
          width: 100px;
          height: 20px;
          position: relative;
        }
        
        .dna-base {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          position: absolute;
        }
        
        .dna-base-left {
          background-color: rgba(59, 130, 246, 0.6);
          left: 0;
        }
        
        .dna-base-right {
          background-color: rgba(16, 185, 129, 0.6);
          right: 0;
        }
        
        .dna-step:nth-child(odd) .dna-base-left {
          left: 20px;
        }
        
        .dna-step:nth-child(odd) .dna-base-right {
          right: 20px;
        }
        
        @keyframes dna-rotate {
          0% { transform: rotateX(0deg); }
          100% { transform: rotateX(360deg); }
        }
      `}</style>
    </div>
  )
}
