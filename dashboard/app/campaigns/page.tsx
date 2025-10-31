"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { MetricCard } from "@/components/metric-card"
import { CampaignService } from "@/lib/campaign-service"
import { FirestoreService } from "@/lib/firestore-service"
import { collection, query, getDocs, orderBy, limit, where, Timestamp } from "firebase/firestore"
import { db } from "@/lib/firebase"

export default function CampaignsPage() {
  const [campaignRunning, setCampaignRunning] = useState(false)
  const [campaignData, setCampaignData] = useState<any[]>([])
  const [stats, setStats] = useState({
    activeCampaigns: 0,
    totalEmailsSent: 0,
    averageSuccessRate: 0,
    qualifiedContacts: 0
  })
  const [loading, setLoading] = useState(true)
  const campaignService = new CampaignService()
  const firestoreService = new FirestoreService()

  useEffect(() => {
    loadCampaignData()
  }, [])

  const loadCampaignData = async () => {
    try {
      setLoading(true)
      
      // Get email stats for the month
      const emailStats = await firestoreService.getEmailStats(30)
      
      // Get recent emails as campaigns
      const recentEmails = await firestoreService.getRecentEmails(20)
      
      // Group emails by date as campaigns
      const campaignsByDate: { [key: string]: any } = {}
      
      recentEmails.forEach((email) => {
        const date = email.sent_at.toDate().toDateString()
        if (!campaignsByDate[date]) {
          campaignsByDate[date] = {
            id: date,
            name: `Daily Campaign - ${date}`,
            emails: [],
            status: 'completed',
            successCount: 0,
            totalCount: 0,
            startTime: email.sent_at
          }
        }
        campaignsByDate[date].emails.push(email)
        campaignsByDate[date].totalCount++
        if (email.status === 'sent') {
          campaignsByDate[date].successCount++
        }
      })
      
      const campaigns = Object.values(campaignsByDate)
      setCampaignData(campaigns)
      
      // Get qualified contacts count
      const contactStats = await firestoreService.getContactStats()
      
      // Calculate stats
      setStats({
        activeCampaigns: campaigns.filter(c => c.status === 'active').length,
        totalEmailsSent: emailStats.totalSent,
        averageSuccessRate: emailStats.successRate,
        qualifiedContacts: contactStats.qualified
      })
      
    } catch (error) {
      console.error('Error loading campaign data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRunCampaign = async (emailCount: number) => {
    setCampaignRunning(true)
    
    try {
      let result = await campaignService.runEmailCampaign(emailCount)
      
      if (!result.success) {
        result = await campaignService.runLocalCampaign(emailCount)
      }
      
      if (result.success) {
        alert(`✅ Campaign Started!\nRunning ${emailCount} emails`)
        // Reload campaign data after running
        setTimeout(() => loadCampaignData(), 3000)
      } else {
        alert(`❌ Campaign Failed\n${result.message}`)
      }
    } catch (error) {
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setCampaignRunning(false)
    }
  }

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight gradient-text">Campaigns</h1>
          <p className="text-muted-foreground mt-1">
            Manage and monitor your AI-powered email campaigns
          </p>
        </div>
        <Button 
          className="glossy-button"
          onClick={() => alert('Custom Campaign Builder coming soon!\n\nFor now, use the Quick Actions below to run campaigns with different email counts.')}
        >
          New Campaign
        </Button>
      </div>

      {/* Campaign Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Campaigns"
          value={stats.activeCampaigns.toString()}
          description="Currently running"
        />
        
        <MetricCard
          title="Total Emails Sent"
          value={stats.totalEmailsSent.toLocaleString()}
          description="This month"
        />
        
        <MetricCard
          title="Average Success Rate"
          value={`${stats.averageSuccessRate.toFixed(1)}%`}
          description="Across all campaigns"
        />
        
        <MetricCard
          title="Qualified Contacts"
          value={stats.qualifiedContacts.toLocaleString()}
          description="Score 7+ ready for outreach"
        />
      </div>

      {/* Campaign List */}
      <div className="metric-card">
        <h3 className="text-lg font-semibold mb-4">Active Campaigns</h3>
        {loading ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Loading campaigns...</p>
          </div>
        ) : campaignData.length === 0 ? (
          <div className="text-center py-12">
            <div className="h-12 w-12 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center text-2xl font-bold text-muted-foreground">
              0
            </div>
            <h4 className="text-lg font-semibold mb-2">No Campaigns</h4>
            <p className="text-muted-foreground mb-4">
              Create your first email campaign to get started.
            </p>
            <Button onClick={() => alert('Custom Campaign Builder coming soon!\n\nFor now, use the Quick Actions below to run campaigns with different email counts.')}>
              Create Campaign
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {campaignData.map((campaign) => (
            <div key={campaign.id} className="p-4 rounded-lg bg-secondary/30 border border-border/50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h4 className="font-semibold text-lg">{campaign.name}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      campaign.status === 'active' 
                        ? 'bg-[#6ad192]/20 text-[#6ad192] border border-[#6ad192]/30' 
                        : 'bg-[#f3d060]/20 text-[#f3d060] border border-[#f3d060]/30'
                    }`}>
                      {campaign.status}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                    <div>
                      <p className="text-xs text-muted-foreground">Emails Sent</p>
                      <p className="font-semibold">{campaign.totalCount || 0}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Success Rate</p>
                      <p className="font-semibold">{campaign.totalCount > 0 ? ((campaign.successCount / campaign.totalCount) * 100).toFixed(1) : '0'}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Qualified</p>
                      <p className="font-semibold">{campaign.successCount || 0}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Next Run</p>
                      <p className="font-semibold text-xs">{campaign.status === 'active' ? 'In Progress' : 'Completed'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex-1 bg-secondary rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all duration-500"
                        style={{ 
                          width: `${campaign.totalCount > 0 ? ((campaign.successCount / campaign.totalCount) * 100) : 0}%` 
                        }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {campaign.successCount || 0}/{campaign.totalCount || 0}
                    </span>
                  </div>
                </div>
                
                <div className="flex gap-2 ml-4">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => alert('Campaign control coming soon! This will allow you to pause/resume individual campaigns.')}
                  >
                    {campaign.status === 'active' ? 'Pause' : 'Resume'}
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => alert(`Campaign Details:\n\nName: ${campaign.name}\nStatus: ${campaign.status}\nEmails Sent: ${campaign.totalCount || 0}\nSuccess Rate: ${campaign.totalCount > 0 ? ((campaign.successCount / campaign.totalCount) * 100).toFixed(1) : '0'}%\n\nDetailed analytics coming soon!`)}
                  >
                    View Details
                  </Button>
                </div>
              </div>
            </div>
          ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Button 
          className="h-20 flex-col gap-2 glossy-button"
          onClick={() => handleRunCampaign(5)}
          disabled={campaignRunning}
        >
          <span className="text-2xl">5</span>
          <span>{campaignRunning ? 'Running...' : 'Run 5 Emails'}</span>
        </Button>
        
        <Button 
          className="h-20 flex-col gap-2 glossy-button"
          onClick={() => handleRunCampaign(25)}
          disabled={campaignRunning}
        >
          <span className="text-2xl">25</span>
          <span>{campaignRunning ? 'Running...' : 'Run 25 Emails'}</span>
        </Button>
        
        <Button 
          className="h-20 flex-col gap-2 glossy-button"
          onClick={() => handleRunCampaign(50)}
          disabled={campaignRunning}
        >
          <span className="text-2xl">50</span>
          <span>{campaignRunning ? 'Running...' : 'Daily Campaign (50)'}</span>
        </Button>
        
        <Button 
          className="h-20 flex-col gap-2 glossy-button"
          onClick={() => alert('Schedule functionality coming soon!')}
        >
          <span className="text-xl">⏰</span>
          <span>Schedule Campaign</span>
        </Button>
      </div>
    </div>
  )
}