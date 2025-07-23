// "use client"

import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Label } from "../components/ui/label"
import { Checkbox } from "../components/ui/checkbox"
import { Card, CardContent, CardFooter } from "../components/ui/card"
import { Eye, EyeOff, User, Lock, AlertCircle, ArrowRight, Microscope } from "lucide-react"
import { cn } from "../lib/utils"
import { Link, useNavigate } from "react-router-dom"
import {useCrossPageNotifications} from "../hooks/use-cross-page-notifications"
import api from "../api"
import { useQueuedNotifications } from "../hooks/use-queued-notifications"
import { ACCESS_TOKEN_LIFETIME } from "../constants"

// Custom hook for login mutation
const useLoginMutation = () => {
  const { showOnNextPage } = useCrossPageNotifications()

  return useMutation({
    mutationFn: async (loginData) => {
      const response = await api.post("auth/user/login/", loginData)
      return response.data
    },
    onSuccess: (data) => {
      if (data.access && data.refresh) {
        const expiryTimestamp = Date.now() + ACCESS_TOKEN_LIFETIME
        localStorage.setItem(ACCESS_TOKEN_LIFETIME, expiryTimestamp)
        localStorage.setItem('ACCESS_TOKEN', data.access)
        localStorage.setItem('REFRESH_TOKEN', data.refresh)
      }
      showOnNextPage({
        type: "success",
        title: "Login successful",
        message: "You have been logged in successfully",
        duration: 3000,
      },
      "/users/",
    )
    },
    onError: (error) => {
      // showOnNextPage({
      //   type: "error",
      //   title: "Login failed",
      //   message: error.response,
      //   duration: 3000,
      // })
      console.error("Login error:", error)
      console.error("Error response:", error.response)
      
      if (error.response) {
        if (error.response.status === 405) {
          console.error("Method not allowed - server doesn't accept POST on this endpoint")
        } else if (error.response.status === 400) {
          const serverErrors = error.response.data
          console.error("Server validation errors:", serverErrors)
        } else if (error.response.status === 401) {
          console.error(error.response.data.detail);

      } else if (error.request) {
        console.error("Network error - no response received")
      } else {
        console.error("Error setting up request:", error.message)
      }
    }}
  })
}

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [formErrors, setFormErrors] = useState({})
  useQueuedNotifications()


  // Use React Query mutation
  const loginMutation = useLoginMutation()
  const isLoading = loginMutation.isPending

  // Form state
  const [loginForm, setLoginForm] = useState({
    username: "",
    password: "",
    rememberMe: false,
  })

  const handleLoginChange = (e) => {
    const { name, value, type, checked } = e.target
    setLoginForm({
      ...loginForm,
      [name]: type === "checkbox" ? checked : value,
    })

    // Clear errors when typing
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: null,
      })
    }
  }

  const validateLoginForm = () => {
    const errors = {}

    if (!loginForm.username) {
      errors.username = "Username is required"
    }

    if (!loginForm.password) {
      errors.password = "Password is required"
    }

    return errors
  }

  const handleLoginSubmit = async (e) => {
    e.preventDefault()
    const errors = validateLoginForm()

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    // Use React Query mutation
    loginMutation.mutate(loginForm)
  }

  const handleGoogleSignIn = () => {
    // Simulate Google sign-in
    console.log("Google sign-in initiated")
    // Here you would typically redirect to Google OAuth flow
  }

  return (
    <div className="min-h-screen bg-white/10 backdrop-blur-md relative overflow-hidden">
      {/* Full background with glass effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-green-500/10 to-green-500/20"></div>

      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Floating particles */}
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white/30 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${4 + Math.random() * 3}s`,
            }}
          />
        ))}

        {/* Large glowing orbs */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl animate-pulse-slow-delay"></div>

        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: "50px 50px",
            animation: "grid-move 30s linear infinite",
          }}
        ></div>
      </div>

      {/* Header */}
      <header className="relative z-20 px-6 py-4 border-b border-white/10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Microscope className="h-8 w-8 text-green-600" />
            <span className="text-2xl font-bold text-gray-900">EpiScope</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/signup" className="text-sm font-medium text-gray-700 hover:text-green-600 transition-colors">
              Sign Up
            </Link>
            <Button size="sm" className="bg-green-600 hover:bg-green-700">
              Sign In
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <div className="relative z-10 flex items-center justify-center min-h-[calc(100vh-80px)] p-6">
        <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left side - Branding */}
          <div className="text-center lg:text-left">
            <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
              Welcome back to{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-green-600">
                EpiScope
              </span>
            </h1>

            <p className="text-gray-700 text-lg mb-8 max-w-md mx-auto lg:mx-0">
              Sign in to access your dashboard and continue monitoring epidemic data in real-time.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg mx-auto lg:mx-0">
              <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg border border-white/20">
                <div className="bg-green-50 p-2 rounded-full w-fit mb-3">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div className="font-medium text-gray-900">Real-time Monitoring</div>
                <div className="text-sm text-gray-600">Track outbreaks as they happen</div>
              </div>

              <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg border border-white/20">
                <div className="bg-green-50 p-2 rounded-full w-fit mb-3">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="font-medium text-gray-900">Instant Alerts</div>
                <div className="text-sm text-gray-600">Get notified of new outbreaks</div>
              </div>
            </div>
          </div>

          {/* Right side - Login form */}
          <div className="flex justify-center lg:justify-end">
            <div className="w-full max-w-md">
              <Card className="backdrop-blur-md bg-white/30 border-white/20 shadow-2xl">
                <CardContent className="pt-6">
                  <div className="text-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Sign In</h2>
                    <p className="text-gray-600 mt-1">Enter your credentials to access your account</p>
                  </div>

                  <form onSubmit={handleLoginSubmit} className="mt-6">
                    <div className="grid gap-6">
                      <div className="grid gap-3">
                        <Label htmlFor="login-username" className="text-sm font-medium text-gray-900">
                          Username
                        </Label>
                        <div className="relative">
                          <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 h-4 w-4" />
                          <Input
                            id="login-username"
                            name="username"
                            type="username"
                            placeholder="username"
                            className={cn(
                              "pl-10 bg-white/50  border-white/30",
                              formErrors.username && "border-red-500 focus-visible:ring-red-500",
                            )}
                            value={loginForm.username}
                            onChange={handleLoginChange}
                          />
                        </div>
                        {formErrors.username && (
                          <div className="flex items-center text-red-600 text-sm">
                            <AlertCircle className="h-4 w-4 mr-1" />
                            {formErrors.username}
                          </div>
                        )}
                      </div>

                      <div className="grid gap-3">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="login-password" className="text-sm font-medium text-gray-900">
                            Password
                          </Label>
                          <a href="#" className="text-sm font-medium text-green-600 hover:text-green-500">
                            Forgot password?
                          </a>
                        </div>
                        <div className="relative">
                          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 h-4 w-4" />
                          <Input
                            id="login-password"
                            name="password"
                            type={showPassword ? "text" : "password"}
                            placeholder="••••••••"
                            className={cn(
                              "pl-10 bg-white/50  border-white/30",
                              formErrors.password && "border-red-500 focus-visible:ring-red-500",
                            )}
                            value={loginForm.password}
                            onChange={handleLoginChange}
                          />
                          <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                          >
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </button>
                        </div>
                        {formErrors.password && (
                          <div className="flex items-center text-red-600 text-sm">
                            <AlertCircle className="h-4 w-4 mr-1" />
                            {formErrors.password}
                          </div>
                        )}
                      </div>

                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="remember-me"
                          name="rememberMe"
                          checked={loginForm.rememberMe}
                          onCheckedChange={(checked) => setLoginForm({ ...loginForm, rememberMe: checked })}
                        />
                        <Label htmlFor="remember-me" className="text-sm font-medium leading-none text-gray-900">
                          Remember me
                        </Label>
                      </div>

                      <Button type="submit" className="w-full bg-green-600 cursor-pointer hover:bg-green-700" disabled={isLoading}>
                        {isLoading ? (
                          <div className="flex items-center">
                            <div className="animate-spin mr-2 h-4 w-4 border-2 border-b-transparent border-white rounded-full"></div>
                            Signing in...
                          </div>
                        ) : (
                          <div className="flex items-center">
                            Sign In
                            <ArrowRight className="ml-2 h-4 w-4" />
                          </div>
                        )}
                      </Button>

                      <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                          <span className="w-full border-t border-white/30"></span>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                          <span className="bg-white/50 px-2 text-gray-600">Or continue with</span>
                        </div>
                      </div>

                      <Button
                        type="button"
                        variant="outline"
                        className="w-full bg-white/50 backdrop-blur-sm border-white/30 hover:bg-white/70"
                        onClick={handleGoogleSignIn}
                        disabled={isLoading}
                      >
                        <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                          <path
                            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            fill="#4285F4"
                          />
                          <path
                            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            fill="#34A853"
                          />
                          <path
                            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                            fill="#FBBC05"
                          />
                          <path
                            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            fill="#EA4335"
                          />
                        </svg>
                        Google
                      </Button>
                    </div>
                  </form>
                </CardContent>
                <CardFooter className="flex justify-center pb-6">
                  <p className="text-sm text-gray-600">
                    Don't have an account?{" "}
                    <Link href="/signup" className="text-green-600 hover:text-green-500 font-medium">
                      Sign up
                    </Link>
                  </p>
                </CardFooter>
              </Card>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes grid-move {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        .animate-float {
          animation: float 8s ease-in-out infinite;
        }
        
        .animate-pulse-slow {
          animation: pulse 10s ease-in-out infinite;
        }
        
        .animate-pulse-slow-delay {
          animation: pulse 10s ease-in-out 5s infinite;
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.8; }
        }
      `}</style>
    </div>
  )
}
