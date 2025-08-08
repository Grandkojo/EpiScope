"use client"

// import { useChat } from "ai/react"
import { useState, useRef, useEffect } from "react"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { ScrollArea } from "../components/ui/scroll-area"
import { Send, Bot, User, Activity, TrendingUp, AlertTriangle } from "lucide-react"

export default function EpiScopeHealthChatbot() {
    const messages = [
        {
            role: "user",
            content: "Hello, how are you?"
            },
        
    ]
    const input = ""
    const handleInputChange = () => {}
    const handleSubmit = () => {}
    const isLoading = false
//   const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat()
  const messagesEndRef = useRef(null)
  const [isMinimized, setIsMinimized] = useState(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const quickQuestions = [
    { icon: TrendingUp, text: "Show diabetes trends", query: "What are the current diabetes trends I should monitor?" },
    { icon: AlertTriangle, text: "Malaria alerts", query: "What malaria indicators should trigger alerts?" },
    { icon: Activity, text: "Health metrics", query: "Explain key health performance metrics" },
  ]

  return (
    <div className="w-full max-w-screen mx-auto bg-gray-50">
      {/* Header matching EpiScope theme */}
      {/* <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">EpiScope Health Assistant</h1>
        <p className="text-gray-600">AI-powered epidemic analysis and monitoring support</p>
      </div> */}

      {/* Main Chat Interface */}
      <Card className="bg-white shadow-lg border-0">
        <CardHeader className="bg-blue-600 text-white rounded-t-lg">
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            Health AI Assistant
            <div className="ml-auto flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm">Online</span>
            </div>
          </CardTitle>
        </CardHeader>

        <CardContent className="p-0">
          {/* Messages Area */}
          <ScrollArea className="h-96 p-4">
            {messages.length === 0 && (
              <div className="text-center py-8">
                <Bot className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Welcome to EpiScope Health AI</h3>
                <p className="text-gray-600 mb-4">
                  I'm here to help with diabetes and malaria epidemic monitoring. Ask me about trends, metrics, or
                  analysis.
                </p>

                {/* Quick Action Buttons */}
                <div className="grid grid-cols-1 gap-2 max-w-sm mx-auto">
                  {quickQuestions.map((question, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      className="flex items-center gap-2 text-left justify-start h-auto p-3 border-blue-200 hover:bg-blue-50 bg-transparent"
                      onClick={() => handleSubmit(new Event("submit"), { data: { message: question.query } })}
                    >
                      <question.icon className="w-4 h-4 text-blue-600" />
                      <span className="text-sm">{question.text}</span>
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div key={index} className={`mb-4 flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`flex items-start gap-2 max-w-[80%] ${message.role === "user" ? "flex-row-reverse" : "flex-row"}`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      message.role === "user" ? "bg-blue-600" : "bg-yellow-500"
                    }`}
                  >
                    {message.role === "user" ? (
                      <User className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-white" />
                    )}
                  </div>
                  <div
                    className={`rounded-lg p-3 ${
                      message.role === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-900 border border-gray-200"
                    }`}
                  >
                    <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-start gap-2">
                  <div className="w-8 h-8 rounded-full bg-yellow-500 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-lg p-3 border border-gray-200">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </ScrollArea>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <Input
                value={input}
                onChange={handleInputChange}
                placeholder="Ask about diabetes trends, malaria indicators, or health metrics..."
                className="flex-1 border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                disabled={isLoading}
              />
              <Button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4"
              >
                <Send className="w-4 h-4" />
              </Button>
            </form>

            {/* Status Bar */}
            <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
              <span>Specialized in diabetes & malaria epidemic monitoring</span>
              <span className="flex items-center gap-1">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                AI Assistant Active
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Indicators matching the dashboard theme */}
      {/* <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-white border-l-4 border-l-blue-600">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-blue-600">98%</div>
            <div className="text-sm text-gray-600">Health Data Accuracy</div>
          </CardContent>
        </Card>
        <Card className="bg-white border-l-4 border-l-yellow-500">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-yellow-600">24/7</div>
            <div className="text-sm text-gray-600">Monitoring Active</div>
          </CardContent>
        </Card>
        <Card className="bg-white border-l-4 border-l-green-500">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-green-600">1.2s</div>
            <div className="text-sm text-gray-600">Response Time</div>
          </CardContent>
        </Card>
        <Card className="bg-white border-l-4 border-l-purple-500">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-purple-600">50+</div>
            <div className="text-sm text-gray-600">Health Indicators</div>
          </CardContent>
        </Card>
      </div> */}
    </div>
  )
}
