"use client"

import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Label } from "../components/ui/label"
import { Checkbox } from "../components/ui/checkbox"
import { Card, CardContent, CardFooter } from "../components/ui/card"
import { Eye, EyeOff, Mail, Lock, User, AlertCircle, ArrowRight, Microscope, PhoneCall, MapPinHouse, ArrowLeft } from "lucide-react"
import { cn } from "../lib/utils"
import { Link, useNavigate } from "react-router-dom"

import api from "../api"

// Custom hook for signup mutation
const useSignupMutation = () => {
  const navigate = useNavigate()
  
  return useMutation({
    mutationFn: async (signupData) => {
      const response = await api.post("auth/user/register/", signupData)
      return response.data
    },
    onSuccess: (data) => {
      console.log("Signup successful:", data)
      navigate("/login")
    },
    onError: (error) => {
      console.error("Signup error:", error)
      console.error("Error response:", error.response)
      
      if (error.response) {
        if (error.response.status === 405) {
          console.error("Method not allowed - server doesn't accept POST on this endpoint")
        } else if (error.response.status === 400) {
          const serverErrors = error.response.data
          console.error("Server validation errors:", serverErrors)
        }
      } else if (error.request) {
        console.error("Network error - no response received")
      } else {
        console.error("Error setting up request:", error.message)
      }
    }
  })
}

export default function SignupPage() {
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const [formErrors, setFormErrors] = useState({})
  const [currentStep, setCurrentStep] = useState(1)

  // Use React Query mutation
  const signupMutation = useSignupMutation()
  const isLoading = signupMutation.isPending

  // Form state
  const [signupForm, setSignupForm] = useState({
    username: "",
    email: "",
    phone: "",
    address: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: false,
  })

  const handleSignupChange = (e) => {
    const { name, value, type, checked } = e.target
    setSignupForm({
      ...signupForm,
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

  const validateFirstStep = () => {
    const errors = {}

    if (!signupForm.username) {
      errors.username = "Username is required"
    }

    if (!signupForm.email) {
      errors.email = "Email is required"
    } else if (!/\S+@\S+\.\S+/.test(signupForm.email)) {
      errors.email = "Email is invalid"
    }

    if (!signupForm.phone) {
      errors.phone = "Phone number is required"
    }

    if (!signupForm.address) {
      errors.address = "Address is required"
    }

    return errors
  }

  const validateSignupForm = () => {
    const errors = {}

    if (!signupForm.username) {
      errors.username = "Username is required"
    }

    if (!signupForm.email) {
      errors.email = "Email is required"
    } else if (!/\S+@\S+\.\S+/.test(signupForm.email)) {
      errors.email = "Email is invalid"
    }

    if (!signupForm.phone) {
      errors.phone = "Phone number is required"
    }

    if (!signupForm.address) {
      errors.address = "Address is required"
    }

    if (!signupForm.password) {
      errors.password = "Password is required"
    } else if (signupForm.password.length < 8) {
      errors.password = "Password must be at least 8 characters"
    } else if (!/(?=.*[A-Z])/.test(signupForm.password)) {
      errors.password = "Password must contain at least one capital letter"
    } else if (!/(?=.*\d)/.test(signupForm.password)) {
      errors.password = "Password must contain at least one number"
    }

    if (!signupForm.confirmPassword) {
      errors.confirmPassword = "Please confirm your password"
    } else if (signupForm.password !== signupForm.confirmPassword) {
      errors.confirmPassword = "Passwords do not match"
    }

    if (!signupForm.agreeToTerms) {
      errors.agreeToTerms = "You must agree to the terms and conditions"
    }

    return errors
  }

  const handleNextStep = () => {
    const errors = validateFirstStep()

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    setCurrentStep(2)
    setFormErrors({})
  }

  const handlePreviousStep = () => {
    setCurrentStep(1)
    setFormErrors({})
  }

  const handleSignupSubmit = async (e) => {
    e.preventDefault()
    const errors = validateSignupForm()

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    // Use React Query mutation
    signupMutation.mutate(signupForm)
  }

  const handleGoogleSignIn = () => {
    // Simulate Google sign-in
    console.log("Google sign-in initiated")
    // Here you would typically redirect to Google OAuth flow
  }

  const isFirstStepValid = () => {
    return signupForm.username && signupForm.email && signupForm.phone && signupForm.address && /\S+@\S+\.\S+/.test(signupForm.email)
  }

  const isSecondStepValid = () => {
    return (
      signupForm.password &&
      signupForm.password.length >= 8 &&
      /(?=.*[A-Z])/.test(signupForm.password) &&
      /(?=.*\d)/.test(signupForm.password) &&
      signupForm.confirmPassword &&
      signupForm.password === signupForm.confirmPassword &&
      signupForm.agreeToTerms
    )
  }

  return (
    <div className="min-h-screen bg-white/10 backdrop-blur-md relative overflow-hidden">
      {/* Full background with glass effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-600/20 via-blue-500/10 to-purple-500/20"></div>

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
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-400/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl animate-pulse-slow-delay"></div>

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
            <Button size="sm" className="bg-green-600 hover:bg-green-700">
              Sign Up
            </Button>
            <Link to="/login" className="text-sm font-medium text-gray-700 hover:text-green-600 transition-colors">
              Sign In
            </Link>
          </div>
        </div>
      </header>

      {/* Main content */}

      <div className="relative z-10 flex items-center justify-center min-h-[calc(100vh-80px)] p-6">
        <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-30 items-center">

          {/* Right side - Branding */}
          <div className="text-center lg:text-left order-1 lg:order-1">
            <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
              Join the{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-green-600">
                EpiScope
              </span>{" "}
              community
            </h1>

            <p className="text-gray-700 text-lg mb-8 max-w-md mx-auto lg:mx-0">
              Create an account to access powerful epidemic monitoring tools and join healthcare professionals
              worldwide.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg mx-auto lg:mx-0">
              <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg border border-white/20">
                <div className="bg-green-100 p-2 rounded-full w-fit mb-3">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="font-medium text-gray-900">Real-time Analytics</div>
                <div className="text-sm text-gray-600">Track disease patterns as they emerge</div>
              </div>

              <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg border border-white/20">
                <div className="bg-green-100 p-2 rounded-full w-fit mb-3">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="font-medium text-gray-900">Predictive Modeling</div>
                <div className="text-sm text-gray-600">Forecast potential outbreak patterns</div>
              </div>

              {/* <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg border border-white/20">
                <div className="bg-purple-100 p-2 rounded-full w-fit mb-3">
                  <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="font-medium text-gray-900">Global Coverage</div>
                <div className="text-sm text-gray-600">Monitor epidemics across 89+ countries</div>
              </div> */}

              {/* <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg border border-white/20">
                <div className="bg-indigo-100 p-2 rounded-full w-fit mb-3">
                  <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="font-medium text-gray-900">Secure Data</div>
                <div className="text-sm text-gray-600">Enterprise-grade security protocols</div>
              </div> */}
            </div>
          </div>
          {/* Left side - Signup form */}
          <div className="flex justify-center lg:justify-start order-2 lg:order-2">
            <div className="w-full max-w-md">
              <Card className="backdrop-blur-md bg-white/30 border-white/20 shadow-2xl">
                <CardContent className="pt-2">
                  <div className="text-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Create an Account</h2>
                    <p className="text-gray-600 mt-1">Join EpiScope to start monitoring epidemic data</p>
                    
                    {/* Step indicators */}
                    <div className="flex items-center justify-center mt-4 space-x-2">
                      <div className={cn(
                        "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
                        currentStep >= 1 ? "bg-green-600 text-white" : "bg-gray-200 text-gray-600"
                      )}>
                        1
                      </div>
                      <div className={cn(
                        "w-12 h-1 rounded",
                        currentStep >= 2 ? "bg-green-600" : "bg-gray-200"
                      )}></div>
                      <div className={cn(
                        "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
                        currentStep >= 2 ? "bg-green-600 text-white" : "bg-gray-200 text-gray-600"
                      )}>
                        2
                      </div>
                    </div>
                  </div>

                  <form onSubmit={handleSignupSubmit} className="mt-6">
                    {currentStep === 1 && (
                      <div className="grid gap-6">
                        <div className="grid gap-4">
                          <Label htmlFor="signup-username" className="text-sm font-medium text-gray-900">
                            Username
                          </Label>
                          <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500  h-4 w-4" />
                            <Input
                              id="signup-username"
                              name="username"
                              type="text"
                              placeholder="John Doe"
                              className={cn(
                                "pl-10 bg-white/50  border-white/30",
                                formErrors.username && "border-red-500 focus-visible:ring-red-500",
                              )}
                              value={signupForm.username}
                              onChange={handleSignupChange}
                            />
                          </div>
                          {formErrors.username && (
                            <div className="flex items-center text-red-600 text-sm">
                              <AlertCircle className="h-4 w-4 mr-1" />
                              {formErrors.username}
                            </div>
                          )}
                        </div>

                        <div className="grid gap-4">
                          <Label htmlFor="signup-email" className="text-sm font-medium text-gray-900">
                            Email
                          </Label>
                          <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 h-4 w-4" />
                            <Input
                              id="signup-email"
                              name="email"
                              type="email"
                              placeholder="name@example.com"
                              className={cn(
                                "pl-10 bg-white/50  border-white/30",
                                formErrors.email && "border-red-500 focus-visible:ring-red-500",
                              )}
                              value={signupForm.email}
                              onChange={handleSignupChange}
                            />
                          </div>
                          {formErrors.email && (
                            <div className="flex items-center text-red-600 text-sm">
                              <AlertCircle className="h-4 w-4 mr-1" />
                              {formErrors.email}
                            </div>
                          )}
                        </div>

                        <div className="grid gap-4">
                          <Label htmlFor="signup-phone" className="text-sm font-medium text-gray-900">
                            Phone Number
                          </Label>
                          <div className="relative">
                            <PhoneCall className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500  h-4 w-4" />
                            <Input
                              id="signup-phone"
                              name="phone"
                              type="text"
                              placeholder="1234567890"
                              className={cn(
                                "pl-10 bg-white/50  border-white/30",
                                formErrors.phone && "border-red-500 focus-visible:ring-red-500",
                              )}
                              value={signupForm.phone}
                              onChange={handleSignupChange}
                            />
                          </div>
                          {formErrors.phone && (
                            <div className="flex items-center text-red-600 text-sm">
                              <AlertCircle className="h-4 w-4 mr-1" />
                              {formErrors.phone}
                            </div>
                          )}
                        </div>

                        <div className="grid gap-4">
                          <Label htmlFor="signup-address" className="text-sm font-medium text-gray-900">
                            Address
                          </Label>
                          <div className="relative">
                            <MapPinHouse className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500  h-4 w-4" />
                            <Input
                              id="signup-address"
                              name="address"
                              type="text"
                              placeholder="1234 Main St, Anytown, USA"
                              className={cn(
                                "pl-10 bg-white/50  border-white/30",
                                formErrors.address && "border-red-500 focus-visible:ring-red-500",
                              )}
                              value={signupForm.address}
                              onChange={handleSignupChange}
                            />
                          </div>
                          {formErrors.address && (
                            <div className="flex items-center text-red-600 text-sm">
                              <AlertCircle className="h-4 w-4 mr-1" />
                              {formErrors.address}
                            </div>
                          )}
                        </div>

                        <Button 
                          type="button" 
                          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed mt-4" 
                          disabled={!isFirstStepValid() || isLoading} 
                          onClick={handleNextStep}
                        >
                          {isLoading ? (
                            <div className="flex items-center">
                              <div className="animate-spin mr-2 h-4 w-4 border-2 border-b-transparent border-white rounded-full"></div>
                              Next
                            </div>
                          ) : (
                            <div className="flex items-center">
                              Next
                              <ArrowRight className="ml-2 h-4 w-4" />
                            </div>
                          )}
                        </Button>
                      </div>
                    )}

                    {currentStep === 2 && (
                      <div className="grid gap-6">
                        <Button 
                          type="button" 
                          variant="outline"
                          size="sm"
                          className="w-fit px-4 py-2 bg-white/50 border-white/30 hover:bg-white/70 mb-2" 
                          onClick={handlePreviousStep}
                        >
                          <ArrowLeft className="mr-2 h-4 w-4" />
                          Back
                        </Button>

                        <div className="grid gap-4">
                          <Label htmlFor="signup-password" className="text-sm font-medium text-gray-900">
                            Password
                          </Label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 h-4 w-4" />
                            <Input
                              id="signup-password"
                              name="password"
                              type={showPassword ? "text" : "password"}
                              placeholder="••••••••"
                              className={cn(
                                "pl-10 bg-white/50  border-white/30",
                                formErrors.password && "border-red-500 focus-visible:ring-red-500",
                              )}
                              value={signupForm.password}
                              onChange={handleSignupChange}
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
                            <div className="flex items-center text-red-500 text-sm">
                              <AlertCircle className="h-4 w-4 mr-1" />
                              {formErrors.password}
                            </div>
                          )}
                          {signupForm.password && !formErrors.password && signupForm.password.length >= 8 && /(?=.*[A-Z])/.test(signupForm.password) && /(?=.*\d)/.test(signupForm.password) && (
                            <div className="flex items-center text-green-600 text-sm">
                              <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              Password meets all requirements
                            </div>
                          )}
                          {signupForm.password && (
                            <div className="text-xs space-y-1">
                              <div className={cn(
                                "flex items-center",
                                signupForm.password.length >= 8 ? "text-green-600" : "text-red-500"
                              )}>
                                <div className={cn(
                                  "w-3 h-3 rounded-full mr-2 flex items-center justify-center",
                                  signupForm.password.length >= 8 ? "bg-green-600" : "bg-red-500"
                                )}>
                                  {signupForm.password.length >= 8 ? (
                                    <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                  ) : (
                                    <div className="w-1 h-1 bg-white rounded-full"></div>
                                  )}
                                </div>
                                At least 8 characters
                              </div>
                              <div className={cn(
                                "flex items-center",
                                /(?=.*[A-Z])/.test(signupForm.password) ? "text-green-600" : "text-red-500"
                              )}>
                                <div className={cn(
                                  "w-3 h-3 rounded-full mr-2 flex items-center justify-center",
                                  /(?=.*[A-Z])/.test(signupForm.password) ? "bg-green-600" : "bg-red-500"
                                )}>
                                  {/(?=.*[A-Z])/.test(signupForm.password) ? (
                                    <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                  ) : (
                                    <div className="w-1 h-1 bg-white rounded-full"></div>
                                  )}
                                </div>
                                At least one capital letter
                              </div>
                              <div className={cn(
                                "flex items-center",
                                /(?=.*\d)/.test(signupForm.password) ? "text-green-600" : "text-red-500"
                              )}>
                                <div className={cn(
                                  "w-3 h-3 rounded-full mr-2 flex items-center justify-center",
                                  /(?=.*\d)/.test(signupForm.password) ? "bg-green-600" : "bg-red-500"
                                )}>
                                  {/(?=.*\d)/.test(signupForm.password) ? (
                                    <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                  ) : (
                                    <div className="w-1 h-1 bg-white rounded-full"></div>
                                  )}
                                </div>
                                At least one number
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="grid gap-4">
                          <Label htmlFor="signup-confirm-password" className="text-sm font-medium text-gray-900">
                            Confirm Password
                          </Label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 h-4 w-4" />
                            <Input
                              id="signup-confirm-password"
                              name="confirmPassword"
                              type={showPassword ? "text" : "password"}
                              placeholder="••••••••"
                              className={cn(
                                "pl-10 bg-white/50  border-white/30",
                                formErrors.confirmPassword && "border-red-500 focus-visible:ring-red-500",
                              )}
                              value={signupForm.confirmPassword}
                              onChange={handleSignupChange}
                            />
                          </div>
                          {formErrors.confirmPassword && (
                            <div className="flex items-center text-red-500 text-sm">
                              <AlertCircle className="h-4 w-4 mr-1" />
                              {formErrors.confirmPassword}
                            </div>
                          )}
                          {signupForm.confirmPassword && !formErrors.confirmPassword && signupForm.password === signupForm.confirmPassword && (
                            <div className="flex items-center text-green-600 text-sm">
                              <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                              Passwords match
                            </div>
                          )}
                          {signupForm.confirmPassword && signupForm.password !== signupForm.confirmPassword && (
                            <div className="flex items-center text-red-500 text-sm">
                              <AlertCircle className="h-4 w-4 mr-1" />
                              Passwords do not match
                            </div>
                          )}
                        </div>

                        <div className="flex items-start space-x-2">
                          <Checkbox
                            id="terms"
                            name="agreeToTerms"
                            checked={signupForm.agreeToTerms}
                            onCheckedChange={(checked) => setSignupForm({ ...signupForm, agreeToTerms: checked })}
                            className={cn(formErrors.agreeToTerms && "border-red-500")}
                          />
                          <div className="grid gap-1.5 leading-none">
                            <Label
                              htmlFor="terms"
                              className={cn(
                                "text-sm font-medium leading-none text-gray-900",
                                formErrors.agreeToTerms && "text-red-600",
                              )}
                            >
                              I agree to the{" "}
                              <a href="#" className="text-green-600 hover:text-green-500">
                                terms of service
                              </a>{" "}
                              and{" "}
                              <a href="#" className="text-green-600 hover:text-green-500">
                                privacy policy
                              </a>
                            </Label>
                            {formErrors.agreeToTerms && (
                              <div className="flex items-center text-red-600 text-xs">
                                <AlertCircle className="h-3 w-3 mr-1" />
                                {formErrors.agreeToTerms}
                              </div>
                            )}
                          </div>
                        </div>

                        <Button 
                          type="submit" 
                          className="w-full bg-green-600 cursor-pointer hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed" 
                          disabled={!isSecondStepValid() || isLoading}
                        >
                          {isLoading ? (
                            <div className="flex items-center">
                              <div className="animate-spin mr-2 h-4 w-4 border-2 border-b-transparent border-white rounded-full"></div>
                              Creating account...
                            </div>
                          ) : (
                            <div className="flex items-center">
                              Create Account
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
                          className="w-full bg-white/50  border-white/30 hover:bg-white/70"
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
                    )}
                  </form>
                </CardContent>
                <CardFooter className="flex justify-center pb-6">
                  <p className="text-sm text-gray-600">
                    Already have an account?{" "}
                    <Link href="/login" className="text-green-600 hover:text-green-500 font-medium">
                      Sign in
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
