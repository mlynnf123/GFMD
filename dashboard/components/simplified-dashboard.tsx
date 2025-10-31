"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { FirestoreService } from "@/lib/firestore-service"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"

import { EmailCampaign, Contact } from "@/lib/firestore-service"

type EmailWithContact = EmailCampaign & { contact?: Contact }

interface DashboardMetrics {
  dailyEmailsSent: number
  emailsRemaining: number
  successRate: number
  totalSent: number
  recentEmails: EmailWithContact[]
}

export function SimplifiedDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    dailyEmailsSent: 0,
    emailsRemaining: 50,
    successRate: 0,
    totalSent: 0,
    recentEmails: []
  })
  
  const [loading, setLoading] = useState(true)
  const [selectedEmail, setSelectedEmail] = useState<EmailWithContact | null>(null)
  const firestoreService = new FirestoreService()

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        // Get email stats and recent emails
        const [emailStats, recentEmails] = await Promise.all([
          firestoreService.getEmailStats(1), // Today only
          firestoreService.getRecentEmails(50) // Last 50 emails
        ])

        setMetrics({
          dailyEmailsSent: emailStats.totalSent,
          emailsRemaining: Math.max(0, 50 - emailStats.totalSent),
          successRate: emailStats.successRate,
          totalSent: emailStats.totalSent,
          recentEmails: recentEmails
        })
        
        setLoading(false)
      } catch (error) {
        console.error('Error loading metrics:', error)
        setLoading(false)
      }
    }

    loadMetrics()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadMetrics, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full"></div>
      </div>
    )
  }

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Email Campaign Dashboard</h1>
          <p className="text-muted-foreground">Track your daily email sending metrics</p>
        </div>
        <Button onClick={() => window.location.reload()}>
          Refresh
        </Button>
      </div>

      {/* Key Metrics - Excel-like layout */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Daily Sent</CardTitle>
            <CardDescription className="text-2xl font-bold">{metrics.dailyEmailsSent}</CardDescription>
          </CardHeader>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Remaining Today</CardTitle>
            <CardDescription className="text-2xl font-bold">{metrics.emailsRemaining}</CardDescription>
          </CardHeader>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CardDescription className="text-2xl font-bold">{Math.round(metrics.successRate)}%</CardDescription>
          </CardHeader>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Sent</CardTitle>
            <CardDescription className="text-2xl font-bold">{metrics.totalSent}</CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Email Log - Excel-like table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Email Activity</CardTitle>
          <CardDescription>Click on any email to view the full content and prompt</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg">
            <div className="grid grid-cols-6 gap-4 p-3 bg-muted/50 border-b font-semibold text-sm">
              <div>Date/Time</div>
              <div>Recipient</div>
              <div>Company</div>
              <div>Subject</div>
              <div>Status</div>
              <div>Score</div>
            </div>
            
            <ScrollArea className="h-[400px]">
              {metrics.recentEmails.map((email) => (
                <div 
                  key={email.id} 
                  className="grid grid-cols-6 gap-4 p-3 border-b hover:bg-muted/30 cursor-pointer transition-colors"
                  onClick={() => setSelectedEmail(email)}
                >
                  <div className="text-sm">
                    {email.sent_at?.toDate?.()?.toLocaleDateString() || 'Recent'}
                    <br />
                    <span className="text-xs text-muted-foreground">
                      {email.sent_at?.toDate?.()?.toLocaleTimeString() || ''}
                    </span>
                  </div>
                  <div className="text-sm">
                    <div className="font-medium">{email.contact?.contact_name || 'Unknown'}</div>
                    <div className="text-xs text-muted-foreground truncate">{email.contact?.email}</div>
                  </div>
                  <div className="text-sm truncate">{email.contact?.company_name || 'Unknown'}</div>
                  <div className="text-sm truncate">{email.subject}</div>
                  <div>
                    <Badge variant={email.status === 'sent' ? 'success' : 'secondary'}>
                      {email.status}
                    </Badge>
                  </div>
                  <div className="text-sm font-mono">{email.contact?.qualification_score?.toFixed(1) || 'N/A'}</div>
                </div>
              ))}
            </ScrollArea>
          </div>
        </CardContent>
      </Card>

      {/* Email Detail Modal */}
      {selectedEmail && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <CardHeader className="flex-row items-center justify-between">
              <div>
                <CardTitle>Email Details</CardTitle>
                <CardDescription>
                  Sent to {selectedEmail.contact?.contact_name} at {selectedEmail.contact?.company_name}
                </CardDescription>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setSelectedEmail(null)}
              >
                ✕
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <strong>Recipient:</strong> {selectedEmail.contact?.email}
                </div>
                <div>
                  <strong>Score:</strong> {selectedEmail.contact?.qualification_score?.toFixed(1) || 'N/A'}
                </div>
                <div>
                  <strong>Sent:</strong> {selectedEmail.sent_at?.toDate?.()?.toLocaleString() || 'Recently'}
                </div>
                <div>
                  <strong>Status:</strong> 
                  <Badge className="ml-2" variant={selectedEmail.status === 'sent' ? 'success' : 'secondary'}>
                    {selectedEmail.status}
                  </Badge>
                </div>
              </div>
              
              <div>
                <strong>Subject:</strong>
                <div className="mt-1 p-2 bg-muted rounded text-sm">{selectedEmail.subject}</div>
              </div>
              
              <div>
                <strong>Email Content:</strong>
                <ScrollArea className="mt-1 p-4 bg-muted rounded h-60">
                  <pre className="text-sm whitespace-pre-wrap">{selectedEmail.body}</pre>
                </ScrollArea>
              </div>
              
              {selectedEmail.campaign_type && (
                <div>
                  <strong>Campaign Type:</strong>
                  <div className="mt-1 p-2 bg-muted/50 rounded text-sm">{selectedEmail.campaign_type}</div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Empty State */}
      {metrics.recentEmails.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-muted-foreground">
              <h3 className="text-lg font-semibold mb-2">No emails sent yet</h3>
              <p>Start your first email campaign to see metrics here.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}