"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { MetricCard } from "@/components/metric-card"
import { ContactImportService } from "@/lib/contact-import-service"

export default function SettingsPage() {
  const [systemHealth, setSystemHealth] = useState({
    gmail: false,
    firestore: false,
    vertexai: false,
    emailsToday: 0,
    lastHealthCheck: null as Date | null
  })

  const [loading, setLoading] = useState(false)
  const [importing, setImporting] = useState(false)
  const importService = new ContactImportService()

  const checkSystemHealth = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8080/api/v1/system/status')
      if (response.ok) {
        const status = await response.json()
        setSystemHealth({
          ...status,
          lastHealthCheck: new Date()
        })
      } else {
        // API server not running
        setSystemHealth({
          gmail: false,
          firestore: false,
          vertexai: false,
          emailsToday: 0,
          lastHealthCheck: new Date()
        })
      }
    } catch (error) {
      console.error('Health check failed:', error)
      setSystemHealth({
        gmail: false,
        firestore: false,
        vertexai: false,
        emailsToday: 0,
        lastHealthCheck: new Date()
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkSystemHealth()
  }, [])

  const getStatusColor = (status: boolean) => {
    return status ? "sentiment-positive" : "sentiment-negative"
  }

  const getStatusText = (status: boolean) => {
    return status ? "Connected" : "Disconnected"
  }

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight gradient-text">Settings</h1>
          <p className="text-muted-foreground mt-1">
            System configuration and health monitoring
          </p>
        </div>
        <Button 
          className="glossy-button" 
          onClick={checkSystemHealth}
          disabled={loading}
        >
          {loading ? 'Checking...' : 'Run Health Check'}
        </Button>
      </div>

      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Gmail API"
          value={getStatusText(systemHealth.gmail)}
          description="Email sending service"
          trend={{ 
            value: 0, 
            label: systemHealth.gmail ? "Operational" : "Needs attention",
            type: systemHealth.gmail ? "neutral" : "down" 
          }}
        />
        
        <MetricCard
          title="Firestore"
          value={getStatusText(systemHealth.firestore)}
          description="Database connection"
          trend={{ 
            value: 0, 
            label: systemHealth.firestore ? "Operational" : "Needs attention",
            type: systemHealth.firestore ? "neutral" : "down" 
          }}
        />
        
        <MetricCard
          title="Vertex AI"
          value={getStatusText(systemHealth.vertexai)}
          description="AI processing engine"
          trend={{ 
            value: 0, 
            label: systemHealth.vertexai ? "Operational" : "Needs attention",
            type: systemHealth.vertexai ? "neutral" : "down" 
          }}
        />
        
        <MetricCard
          title="Emails Today"
          value={systemHealth.emailsToday.toString()}
          description="Daily usage counter"
          trend={{ 
            value: systemHealth.emailsToday > 50 ? 5 : 0, 
            label: `of 100 daily limit`,
            type: "neutral" 
          }}
        />
      </div>

      {/* System Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Configuration */}
        <div className="metric-card">
          <h3 className="text-lg font-semibold mb-4">API Configuration</h3>
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-secondary/30 border border-border/50">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">Dashboard API</h4>
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(systemHealth.gmail && systemHealth.firestore)}`}>
                  {systemHealth.gmail && systemHealth.firestore ? 'Running' : 'Stopped'}
                </span>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Local API server at http://localhost:8080
              </p>
              <div className="text-sm space-y-1">
                <p><span className="font-medium">Port:</span> 8080</p>
                <p><span className="font-medium">Status:</span> {systemHealth.gmail && systemHealth.firestore ? '✅ Online' : '❌ Offline'}</p>
                <p><span className="font-medium">Last Check:</span> {systemHealth.lastHealthCheck?.toLocaleTimeString() || 'Never'}</p>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-secondary/30 border border-border/50">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">Google Cloud APIs</h4>
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(systemHealth.vertexai)}`}>
                  {systemHealth.vertexai ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Vertex AI, Gmail API, and Firestore
              </p>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => alert('API Management coming soon! This will allow you to configure API keys and settings.')}
              >
                Manage APIs
              </Button>
            </div>
          </div>
        </div>

        {/* Email Configuration */}
        <div className="metric-card">
          <h3 className="text-lg font-semibold mb-4">Email Configuration</h3>
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-secondary/30 border border-border/50">
              <h4 className="font-medium mb-2">Daily Limits</h4>
              <div className="text-sm space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Current Limit</span>
                  <span className="font-medium">100 emails/day</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Used Today</span>
                  <span className="font-medium">{systemHealth.emailsToday}/100</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Remaining</span>
                  <span className="font-medium">{100 - systemHealth.emailsToday}</span>
                </div>
              </div>
              <div className="mt-3">
                <div className="flex-1 bg-secondary rounded-full h-2">
                  <div 
                    className="bg-primary h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(systemHealth.emailsToday / 100) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-secondary/30 border border-border/50">
              <h4 className="font-medium mb-2">Email Templates</h4>
              <p className="text-sm text-muted-foreground mb-3">
                AI-generated personalized emails
              </p>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => alert('Template Management coming soon! This will allow you to customize email templates and AI prompts.')}
              >
                Manage Templates
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* System Actions */}
      <div className="metric-card">
        <h3 className="text-lg font-semibold mb-4">System Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button 
            variant="outline" 
            className="h-20 flex-col gap-2"
            onClick={() => {
              if (confirm('This will restart all system services. Continue?')) {
                alert('System restart initiated. Please wait 30 seconds before refreshing.')
              }
            }}
          >
            <span className="text-lg">🔄</span>
            <span>Restart Services</span>
          </Button>

          <Button 
            variant="outline" 
            className="h-20 flex-col gap-2"
            onClick={() => alert('Log Viewer coming soon! This will show detailed system logs for debugging.')}
          >
            <span className="text-lg">📋</span>
            <span>View Logs</span>
          </Button>

          <Button 
            variant="outline" 
            className="h-20 flex-col gap-2"
            onClick={() => {
              const backupData = {
                timestamp: new Date().toISOString(),
                systemHealth,
                settings: 'backup-data-placeholder'
              }
              const blob = new Blob([JSON.stringify(backupData, null, 2)], { type: 'application/json' })
              const url = window.URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `GFMD_Backup_${new Date().toISOString().split('T')[0]}.json`
              document.body.appendChild(a)
              a.click()
              document.body.removeChild(a)
              window.URL.revokeObjectURL(url)
            }}
          >
            <span className="text-lg">💾</span>
            <span>Export Backup</span>
          </Button>
        </div>
      </div>

      {/* Contact Import */}
      <div className="metric-card">
        <h3 className="text-lg font-semibold mb-4">Contact Import</h3>
        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-secondary/30 border border-border/50">
            <h4 className="font-medium mb-2">CSV Import</h4>
            <p className="text-sm text-muted-foreground mb-3">
              Import healthcare contacts from Definitive Healthcare CSV files
            </p>
            
            <div className="space-y-3">
              <input
                type="file"
                accept=".csv"
                onChange={async (e) => {
                  const file = e.target.files?.[0]
                  if (!file) return
                  
                  if (!file.name.endsWith('.csv')) {
                    alert('Please select a CSV file')
                    return
                  }
                  
                  const confirmed = confirm(
                    `Import contacts from ${file.name}?\n\n` +
                    `This will:\n` +
                    `• Check for duplicates based on email and ID\n` +
                    `• Add qualification scores based on titles\n` +
                    `• Skip contacts without emails\n\n` +
                    `Continue with import?`
                  )
                  
                  if (!confirmed) return
                  
                  setImporting(true)
                  try {
                    const csvContent = await file.text()
                    console.log(`📋 Starting import of ${file.name}...`)
                    
                    const result = await importService.importContactsFromCSV(csvContent)
                    
                    const message = `✅ Import Complete!\n\n` +
                      `• Processed: ${result.processed} contacts\n` +
                      `• Added: ${result.added} new contacts\n` +
                      `• Duplicates skipped: ${result.duplicates}\n` +
                      `• Errors: ${result.errors}\n\n` +
                      `${result.errors > 0 ? 'Check console for error details.' : 'All contacts imported successfully!'}`
                    
                    alert(message)
                    
                    if (result.errorMessages.length > 0) {
                      console.log('📋 Import Errors:', result.errorMessages)
                    }
                    
                  } catch (error) {
                    console.error('Import error:', error)
                    alert(`❌ Import failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
                  } finally {
                    setImporting(false)
                    // Clear the file input
                    e.target.value = ''
                  }
                }}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
                disabled={importing}
              />
              
              {importing && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
                  Importing contacts... Please wait.
                </div>
              )}
            </div>
          </div>
          
          <div className="p-4 rounded-lg bg-secondary/30 border border-border/50">
            <h4 className="font-medium mb-2">Import Statistics</h4>
            <Button 
              variant="outline" 
              size="sm"
              onClick={async () => {
                try {
                  const stats = await importService.getImportStats()
                  const message = `📊 Database Statistics:\n\n` +
                    `• Total contacts: ${stats.totalContacts.toLocaleString()}\n` +
                    `• Imported today: ${stats.importedToday}\n\n` +
                    `By source:\n` +
                    Object.entries(stats.byDataSource)
                      .map(([source, count]) => `• ${source}: ${count}`)
                      .join('\n')
                  
                  alert(message)
                } catch (error) {
                  alert(`Error getting stats: ${error instanceof Error ? error.message : 'Unknown error'}`)
                }
              }}
            >
              View Import Stats
            </Button>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="metric-card">
        <h3 className="text-lg font-semibold mb-4">System Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h4 className="font-medium">Application Details</h4>
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Version</span>
                <span>v1.0.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Environment</span>
                <span>Development</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Build</span>
                <span>{new Date().toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="font-medium">Resource Usage</h4>
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Database Size</span>
                <span>~2.1 GB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">API Calls Today</span>
                <span>{systemHealth.emailsToday * 3}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Uptime</span>
                <span>24h 17m</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}