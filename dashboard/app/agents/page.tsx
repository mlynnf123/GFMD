"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { MetricCard } from "@/components/metric-card"
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, BarChart, Bar } from "recharts"

// Real agent data will come from monitoring system
const agentPerformanceData: any[] = []
const tokenUsageData: any[] = []
const agents: any[] = []

export default function AgentsPage() {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "sentiment-positive"
      case "idle": return "sentiment-neutral"
      case "error": return "sentiment-negative"
      default: return "sentiment-neutral"
    }
  }

  const totalTokenUsage = tokenUsageData.reduce((sum, agent) => sum + agent.tokens, 0)
  const totalCost = tokenUsageData.reduce((sum, agent) => sum + agent.cost, 0)

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight gradient-text">AI Agents</h1>
          <p className="text-muted-foreground mt-1">
            Monitor and manage your AI agent swarm performance
          </p>
        </div>
        <Button 
          className="glossy-button"
          onClick={async () => {
            try {
              const response = await fetch('http://localhost:8080/api/v1/system/status')
              if (response.ok) {
                const status = await response.json()
                alert(`System Status:

Gmail API: ${status.gmail ? '✅ Connected' : '❌ Disconnected'}
Firestore: ${status.firestore ? '✅ Connected' : '❌ Disconnected'}
Vertex AI: ${status.vertexai ? '✅ Connected' : '❌ Disconnected'}
Emails Today: ${status.emailsToday || 0}`)
              } else {
                alert('❌ System Health Check Failed\\n\\nAPI server not responding. Please ensure the dashboard API is running:\\n\\ncd /Users/merandafreiner/gfmd_swarm_agent\\npython3 dashboard_api.py')
              }
            } catch (error) {
              alert('❌ Connection Error\\n\\nCannot connect to system health API. Please ensure the dashboard API server is running on port 8080.')
            }
          }}
        >
          System Health Check
        </Button>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Agents"
          value="4/4"
          description="All systems operational"
          trend={{ value: 0, label: "100% uptime", type: "neutral" }}
        />
        
        <MetricCard
          title="Avg Response Time"
          value="2.2s"
          description="Across all agents"
          trend={{ value: -15, label: "vs last week", type: "up" }}
        />
        
        <MetricCard
          title="Requests Processed"
          value="4,384"
          description="Today"
          trend={{ value: 23, label: "vs yesterday", type: "up" }}
        />
        
        <MetricCard
          title="Success Rate"
          value="96.7%"
          description="Average across agents"
          trend={{ value: 2, label: "vs last week", type: "up" }}
        />
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agent Performance Timeline */}
        <div className="metric-card">
          <h3 className="text-lg font-semibold mb-4">24-Hour Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={agentPerformanceData}>
              <XAxis dataKey="time" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Line type="monotone" dataKey="coordinator" stroke="#6ad192" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="research" stroke="#70a9ff" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="qualification" stroke="#f3d060" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="email" stroke="#e27d73" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#6ad192]" />
              <span className="text-sm">Coordinator</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#70a9ff]" />
              <span className="text-sm">Research</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#f3d060]" />
              <span className="text-sm">Qualification</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#e27d73]" />
              <span className="text-sm">Email Composer</span>
            </div>
          </div>
        </div>

        {/* Token Usage & Costs */}
        <div className="metric-card">
          <h3 className="text-lg font-semibold mb-4">Token Usage & Costs (Today)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={tokenUsageData}>
              <XAxis dataKey="agent" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Bar dataKey="tokens" fill="#70a9ff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-border/50">
            <div>
              <p className="text-sm text-muted-foreground">Total Tokens</p>
              <p className="text-lg font-semibold">{totalTokenUsage.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Cost</p>
              <p className="text-lg font-semibold">${totalCost.toFixed(2)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Details */}
      <div className="metric-card">
        <h3 className="text-lg font-semibold mb-4">Agent Status & Performance</h3>
        <div className="space-y-4">
          {agents.map((agent) => (
            <div key={agent.id} className="p-4 rounded-lg bg-secondary/30 border border-border/50">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className="h-12 w-12 rounded-lg bg-primary/20 flex items-center justify-center text-xl font-bold">
                    {agent.id.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h4 className="font-semibold">{agent.name}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
                        {agent.status}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{agent.description}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Uptime</p>
                        <p className="font-semibold text-[#6ad192]">{agent.uptime}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Avg Response</p>
                        <p className="font-semibold">{agent.avgResponseTime}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Requests</p>
                        <p className="font-semibold">{agent.requestsProcessed.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Success Rate</p>
                        <p className="font-semibold">{agent.successRate}%</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => alert('Agent Logs feature coming soon! This will show detailed execution logs for debugging and monitoring.')}
                  >
                    View Logs
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => alert('Agent Configuration coming soon! This will allow you to adjust agent parameters and behavior.')}
                  >
                    Configure
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Resource Usage */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Memory Usage"
          value="68%"
          description="Cloud Run containers"
          chart={
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-secondary rounded-full h-2">
                <div className="bg-primary h-2 rounded-full transition-all duration-500" style={{ width: "68%" }} />
              </div>
              <span className="text-xs text-muted-foreground">MEM</span>
            </div>
          }
        />
        
        <MetricCard
          title="CPU Usage"
          value="45%"
          description="Average across instances"
          chart={
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-secondary rounded-full h-2">
                <div className="bg-[#f3d060] h-2 rounded-full transition-all duration-500" style={{ width: "45%" }} />
              </div>
              <span className="text-xs text-muted-foreground">CPU</span>
            </div>
          }
        />
        
        <MetricCard
          title="Request Queue"
          value="12"
          description="Pending requests"
          chart={
            <div className="flex gap-1">
              {Array.from({ length: 8 }).map((_, i) => {
                const queueHeights = [20, 45, 30, 80, 60, 25, 70, 40] // Fixed queue heights
                return (
                  <div key={i} className="flex-1 h-8 bg-secondary/50 rounded">
                    <div 
                      className="bg-[#70a9ff] h-full rounded transition-all duration-500"
                      style={{ height: `${queueHeights[i]}%` }}
                    />
                  </div>
                )
              })}
            </div>
          }
        />
      </div>
    </div>
  )
}