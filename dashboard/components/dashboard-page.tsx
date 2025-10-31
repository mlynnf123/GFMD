"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { MetricCard } from "@/components/metric-card"
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from "recharts"
import { Play, Zap, Mail, Users, Bot, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

// Mock data - will be replaced with real Firestore data
const emailTrendData = [
  { day: "Mon", sent: 42, success: 38 },
  { day: "Tue", sent: 38, success: 35 },
  { day: "Wed", sent: 45, success: 43 },
  { day: "Thu", sent: 50, success: 47 },
  { day: "Fri", sent: 48, success: 45 },
  { day: "Sat", sent: 35, success: 32 },
  { day: "Sun", sent: 28, success: 26 },
]

const qualificationData = [
  { score: "High (8-10)", value: 145, color: "#6ad192" },
  { score: "Medium (6-7)", value: 230, color: "#70a9ff" },
  { score: "Low (0-5)", value: 89, color: "#e27d73" },
]

const recentEmails = [
  {
    id: 1,
    name: "Dr. Sarah Johnson",
    organization: "Houston Methodist",
    status: "sent",
    time: "2 minutes ago",
    sentiment: "positive"
  },
  {
    id: 2,
    name: "Dr. Michael Chen", 
    organization: "Cleveland Clinic",
    status: "sent",
    time: "5 minutes ago",
    sentiment: "neutral"
  },
  {
    id: 3,
    name: "Jennifer Martinez",
    organization: "Mayo Clinic", 
    status: "sent",
    time: "8 minutes ago",
    sentiment: "positive"
  }
]

export function DashboardPage() {
  const [dailyStats, setDailyStats] = useState({
    emailsSent: 56,
    emailsRemaining: 44,
    successRate: 94,
    contactsProcessed: 15,
    agentsActive: 4,
    avgQualScore: 7.2
  })

  const [systemStatus, setSystemStatus] = useState({
    gmail: "connected",
    firestore: "connected", 
    vertexai: "connected",
    cloudrun: "connected"
  })

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight gradient-text">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Your GFMD AI Swarm Agent campaign overview
          </p>
        </div>
        <Button 
          className="glossy-button gap-2"
          onClick={() => window.location.href = '/campaigns'}
        >
          <Play className="h-4 w-4" />
          Run Campaign
        </Button>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-4 gap-4">
        {Object.entries(systemStatus).map(([service, status]) => (
          <div key={service} className="glass p-2 rounded-lg border border-white/10">
            <div className="flex items-center gap-2">
              <div className={cn(
                "h-2 w-2 rounded-full",
                status === "connected" ? "bg-[#6ad192]" : "bg-[#e27d73]"
              )} />
              <span className="text-xs font-medium capitalize">{service}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <MetricCard
          title="Daily Email Progress"
          value={`${dailyStats.emailsSent}/100`}
          description={`${dailyStats.emailsRemaining} emails remaining today`}
          trend={{
            value: 12,
            label: "vs yesterday", 
            type: "up"
          }}
          chart={
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-secondary rounded-full h-2">
                <div 
                  className="bg-primary h-2 rounded-full transition-all duration-500"
                  style={{ width: `${(dailyStats.emailsSent / 100) * 100}%` }}
                />
              </div>
              <span className="text-xs text-muted-foreground">{dailyStats.emailsSent}%</span>
            </div>
          }
        />

        <MetricCard
          title="Success Rate"
          value={`${dailyStats.successRate}%`}
          description="Email delivery success"
          trend={{
            value: 2,
            label: "vs last week",
            type: "up"
          }}
          chart={
            <ResponsiveContainer width="100%" height={60}>
              <LineChart data={emailTrendData}>
                <Line 
                  type="monotone" 
                  dataKey="success" 
                  stroke="#6ad192" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          }
        />

        <MetricCard
          title="AI Agents Active"
          value={dailyStats.agentsActive}
          description="Processing pipeline"
          chart={
            <div className="flex gap-1">
              {Array.from({ length: 4 }).map((_, i) => {
                const heights = [85, 70, 90, 65] // Fixed heights for each agent
                return (
                  <div key={i} className="flex-1 space-y-1">
                    <div className="h-8 bg-primary/20 rounded">
                      <div 
                        className="bg-primary h-full rounded transition-all duration-500"
                        style={{ height: `${heights[i]}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground block text-center">
                      A{i + 1}
                    </span>
                  </div>
                )
              })}
            </div>
          }
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Email Trends */}
        <div className="metric-card">
          <h3 className="text-lg font-semibold mb-4">Weekly Email Trends</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={emailTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="day" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Bar dataKey="sent" fill="#70a9ff" radius={[2, 2, 0, 0]} />
              <Bar dataKey="success" fill="#6ad192" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Lead Qualification */}
        <div className="metric-card">
          <h3 className="text-lg font-semibold mb-4">Contact Qualification</h3>
          <div className="flex items-center justify-between">
            <ResponsiveContainer width="60%" height={200}>
              <PieChart>
                <Pie
                  data={qualificationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  dataKey="value"
                >
                  {qualificationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {qualificationData.map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div 
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <div className="text-sm">
                    <span className="font-medium">{item.score}</span>
                    <div className="text-muted-foreground">{item.value} contacts</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="metric-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Recent Email Activity</h3>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => window.location.href = '/campaigns'}
          >
            View all
          </Button>
        </div>
        <div className="space-y-3">
          {recentEmails.map((email) => (
            <div key={email.id} className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <Mail className="h-4 w-4" />
                </div>
                <div>
                  <p className="font-medium">{email.name}</p>
                  <p className="text-sm text-muted-foreground">{email.organization}</p>
                </div>
              </div>
              <div className="text-right">
                <div className={cn(
                  "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border",
                  email.sentiment === "positive" && "sentiment-positive",
                  email.sentiment === "neutral" && "sentiment-neutral"
                )}>
                  {email.status}
                </div>
                <p className="text-xs text-muted-foreground mt-1">{email.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}