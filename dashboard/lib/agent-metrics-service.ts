import { 
  collection, 
  addDoc,
  query,
  where,
  orderBy,
  limit,
  getDocs,
  Timestamp,
  doc,
  updateDoc
} from 'firebase/firestore'
import { db } from './firebase'

export interface AgentMetric {
  id?: string
  agent_name: 'coordinator' | 'research' | 'qualification' | 'email_composer'
  action_type: 'email_sent' | 'email_failed' | 'lead_researched' | 'lead_qualified' | 'follow_up_scheduled' | 'response_received' | 'opportunity_created'
  contact_id?: string
  campaign_id?: string
  success: boolean
  duration_ms: number
  timestamp: Timestamp
  metadata: {
    [key: string]: any
  }
  error_message?: string
}

export interface CampaignMetrics {
  total_attempts: number
  successful_sends: number
  failed_sends: number
  response_rate: number
  follow_ups_scheduled: number
  opportunities_created: number
  avg_response_time_hours: number
  agent_performance: {
    [agentName: string]: {
      total_actions: number
      success_rate: number
      avg_duration_ms: number
    }
  }
}

export class AgentMetricsService {
  
  async trackAgentAction(metric: Omit<AgentMetric, 'id' | 'timestamp'>): Promise<void> {
    try {
      const metricWithTimestamp: Omit<AgentMetric, 'id'> = {
        ...metric,
        timestamp: Timestamp.now()
      }
      
      await addDoc(collection(db, 'agent_metrics'), metricWithTimestamp)
      console.log(`✅ Tracked ${metric.agent_name} action: ${metric.action_type}`)
    } catch (error) {
      console.error('Error tracking agent metric:', error)
    }
  }
  
  async trackEmailSent(agentName: 'coordinator' | 'email_composer', contactId: string, campaignId: string, duration: number, success: boolean, error?: string): Promise<void> {
    await this.trackAgentAction({
      agent_name: agentName,
      action_type: success ? 'email_sent' : 'email_failed',
      contact_id: contactId,
      campaign_id: campaignId,
      success,
      duration_ms: duration,
      metadata: {
        delivery_method: 'frontend_campaign',
        timestamp_readable: new Date().toISOString()
      },
      error_message: error
    })
  }
  
  async trackLeadResearch(contactId: string, researchData: any, duration: number, success: boolean): Promise<void> {
    await this.trackAgentAction({
      agent_name: 'research',
      action_type: 'lead_researched',
      contact_id: contactId,
      success,
      duration_ms: duration,
      metadata: {
        research_points: researchData.research_points || 0,
        data_sources: researchData.sources || [],
        enrichment_score: researchData.enrichment_score || 0
      }
    })
  }
  
  async trackLeadQualification(contactId: string, qualificationScore: number, duration: number, success: boolean): Promise<void> {
    await this.trackAgentAction({
      agent_name: 'qualification',
      action_type: 'lead_qualified',
      contact_id: contactId,
      success,
      duration_ms: duration,
      metadata: {
        qualification_score: qualificationScore,
        qualification_criteria: {
          company_size: qualificationScore > 7,
          decision_maker: qualificationScore > 8,
          budget_fit: qualificationScore > 6,
          timing: qualificationScore > 5
        }
      }
    })
  }
  
  async trackFollowUpScheduled(contactId: string, followUpDate: Date, campaignId: string): Promise<void> {
    await this.trackAgentAction({
      agent_name: 'coordinator',
      action_type: 'follow_up_scheduled',
      contact_id: contactId,
      campaign_id: campaignId,
      success: true,
      duration_ms: 250, // Scheduling is quick
      metadata: {
        follow_up_date: followUpDate.toISOString(),
        follow_up_type: 'automated_sequence',
        days_from_initial: Math.ceil((followUpDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
      }
    })
  }
  
  async trackResponseReceived(contactId: string, campaignId: string, responseTime: number): Promise<void> {
    await this.trackAgentAction({
      agent_name: 'coordinator',
      action_type: 'response_received',
      contact_id: contactId,
      campaign_id: campaignId,
      success: true,
      duration_ms: responseTime,
      metadata: {
        response_time_hours: responseTime / (1000 * 60 * 60),
        response_type: 'email_reply',
        sentiment: 'positive' // Would be analyzed by AI
      }
    })
  }
  
  async trackOpportunityCreated(contactId: string, opportunityValue: number, campaignId: string): Promise<void> {
    await this.trackAgentAction({
      agent_name: 'coordinator',
      action_type: 'opportunity_created',
      contact_id: contactId,
      campaign_id: campaignId,
      success: true,
      duration_ms: 500,
      metadata: {
        estimated_value: opportunityValue,
        opportunity_stage: 'initial_interest',
        source_campaign: campaignId
      }
    })
  }
  
  async getCampaignMetrics(campaignId?: string, days: number = 30): Promise<CampaignMetrics> {
    try {
      const metricsRef = collection(db, 'agent_metrics')
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)
      
      let q = query(
        metricsRef,
        where('timestamp', '>=', Timestamp.fromDate(startDate)),
        orderBy('timestamp', 'desc')
      )
      
      // If specific campaign, filter by campaign_id
      if (campaignId) {
        q = query(
          metricsRef,
          where('campaign_id', '==', campaignId),
          where('timestamp', '>=', Timestamp.fromDate(startDate)),
          orderBy('timestamp', 'desc')
        )
      }
      
      const snapshot = await getDocs(q)
      const metrics: AgentMetric[] = []
      
      snapshot.forEach((doc) => {
        metrics.push({ id: doc.id, ...doc.data() } as AgentMetric)
      })
      
      return this.calculateCampaignMetrics(metrics)
    } catch (error) {
      console.error('Error getting campaign metrics:', error)
      return this.getEmptyMetrics()
    }
  }
  
  private calculateCampaignMetrics(metrics: AgentMetric[]): CampaignMetrics {
    const emailSentMetrics = metrics.filter(m => m.action_type === 'email_sent')
    const emailFailedMetrics = metrics.filter(m => m.action_type === 'email_failed')
    const responseMetrics = metrics.filter(m => m.action_type === 'response_received')
    const followUpMetrics = metrics.filter(m => m.action_type === 'follow_up_scheduled')
    const opportunityMetrics = metrics.filter(m => m.action_type === 'opportunity_created')
    
    const totalAttempts = emailSentMetrics.length + emailFailedMetrics.length
    const successfulSends = emailSentMetrics.length
    const failedSends = emailFailedMetrics.length
    
    // Calculate response rate
    const responseRate = successfulSends > 0 ? (responseMetrics.length / successfulSends) * 100 : 0
    
    // Calculate average response time
    const avgResponseTime = responseMetrics.length > 0 
      ? responseMetrics.reduce((sum, metric) => sum + (metric.metadata.response_time_hours || 0), 0) / responseMetrics.length
      : 0
    
    // Calculate agent performance
    const agentPerformance: { [agentName: string]: { total_actions: number, success_rate: number, avg_duration_ms: number } } = {}
    
    const agents = ['coordinator', 'research', 'qualification', 'email_composer'] as const
    
    agents.forEach(agent => {
      const agentMetrics = metrics.filter(m => m.agent_name === agent)
      const successfulActions = agentMetrics.filter(m => m.success).length
      const avgDuration = agentMetrics.length > 0 
        ? agentMetrics.reduce((sum, m) => sum + m.duration_ms, 0) / agentMetrics.length
        : 0
      
      agentPerformance[agent] = {
        total_actions: agentMetrics.length,
        success_rate: agentMetrics.length > 0 ? (successfulActions / agentMetrics.length) * 100 : 0,
        avg_duration_ms: avgDuration
      }
    })
    
    return {
      total_attempts: totalAttempts,
      successful_sends: successfulSends,
      failed_sends: failedSends,
      response_rate: responseRate,
      follow_ups_scheduled: followUpMetrics.length,
      opportunities_created: opportunityMetrics.length,
      avg_response_time_hours: avgResponseTime,
      agent_performance: agentPerformance
    }
  }
  
  private getEmptyMetrics(): CampaignMetrics {
    return {
      total_attempts: 0,
      successful_sends: 0,
      failed_sends: 0,
      response_rate: 0,
      follow_ups_scheduled: 0,
      opportunities_created: 0,
      avg_response_time_hours: 0,
      agent_performance: {
        coordinator: { total_actions: 0, success_rate: 0, avg_duration_ms: 0 },
        research: { total_actions: 0, success_rate: 0, avg_duration_ms: 0 },
        qualification: { total_actions: 0, success_rate: 0, avg_duration_ms: 0 },
        email_composer: { total_actions: 0, success_rate: 0, avg_duration_ms: 0 }
      }
    }
  }
  
  async getAgentPerformanceMetrics(agentName: string, days: number = 7): Promise<{
    total_actions: number
    success_rate: number
    avg_duration_ms: number
    actions_by_hour: { hour: number, count: number }[]
    recent_actions: AgentMetric[]
  }> {
    try {
      const metricsRef = collection(db, 'agent_metrics')
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)
      
      const q = query(
        metricsRef,
        where('agent_name', '==', agentName),
        where('timestamp', '>=', Timestamp.fromDate(startDate)),
        orderBy('timestamp', 'desc'),
        limit(100)
      )
      
      const snapshot = await getDocs(q)
      const metrics: AgentMetric[] = []
      
      snapshot.forEach((doc) => {
        metrics.push({ id: doc.id, ...doc.data() } as AgentMetric)
      })
      
      const successfulActions = metrics.filter(m => m.success).length
      const avgDuration = metrics.length > 0 
        ? metrics.reduce((sum, m) => sum + m.duration_ms, 0) / metrics.length
        : 0
      
      // Actions by hour of day
      const actionsByHour: { [hour: number]: number } = {}
      metrics.forEach(metric => {
        const hour = metric.timestamp.toDate().getHours()
        actionsByHour[hour] = (actionsByHour[hour] || 0) + 1
      })
      
      const actionsHourArray = Object.entries(actionsByHour).map(([hour, count]) => ({
        hour: parseInt(hour),
        count
      }))
      
      return {
        total_actions: metrics.length,
        success_rate: metrics.length > 0 ? (successfulActions / metrics.length) * 100 : 0,
        avg_duration_ms: avgDuration,
        actions_by_hour: actionsHourArray,
        recent_actions: metrics.slice(0, 10)
      }
    } catch (error) {
      console.error('Error getting agent performance:', error)
      return {
        total_actions: 0,
        success_rate: 0,
        avg_duration_ms: 0,
        actions_by_hour: [],
        recent_actions: []
      }
    }
  }
  
  async scheduleFollowUp(contactId: string, campaignId: string, daysFromNow: number = 3): Promise<void> {
    const followUpDate = new Date()
    followUpDate.setDate(followUpDate.getDate() + daysFromNow)
    
    // Create follow-up record
    await addDoc(collection(db, 'scheduled_follow_ups'), {
      contact_id: contactId,
      campaign_id: campaignId,
      scheduled_date: Timestamp.fromDate(followUpDate),
      status: 'scheduled',
      follow_up_type: 'automated_sequence',
      created_at: Timestamp.now()
    })
    
    // Track the scheduling action
    await this.trackFollowUpScheduled(contactId, followUpDate, campaignId)
  }
}