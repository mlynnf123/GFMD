import { 
  collection, 
  query, 
  where, 
  orderBy, 
  limit, 
  getDocs, 
  addDoc,
  updateDoc,
  doc,
  Timestamp 
} from 'firebase/firestore'
import { db } from './firebase'
import { Contact } from './firestore-service'
import { AgentMetricsService } from './agent-metrics-service'

export interface CampaignResult {
  success: boolean
  message: string
  emailsSent: number
  errors: string[]
  selectedContacts: Contact[]
}

export class FrontendCampaignService {
  private metricsService = new AgentMetricsService()
  
  async runEmailCampaign(emailCount: number = 50): Promise<CampaignResult> {
    const campaignId = `campaign_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const campaignStartTime = Date.now()
    
    try {
      console.log(`🚀 Starting backend-powered campaign ${campaignId} for ${emailCount} emails...`)
      
      // Try the main backend API first, fallback to demo if needed
      let response = await fetch('http://localhost:8080/api/v1/automation/quick-run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          num_emails: emailCount
        })
      })
      
      // If main API fails, try the demo API
      if (!response.ok) {
        console.log('🔄 Main API failed, trying demo API...')
        response = await fetch('http://localhost:8081/api/v1/automation/demo-campaign', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            num_emails: emailCount
          })
        })
      }
      
      if (!response.ok) {
        throw new Error(`Both APIs failed: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (!result.success) {
        return {
          success: false,
          message: result.message || 'Campaign failed',
          emailsSent: 0,
          errors: [result.message || 'Unknown error'],
          selectedContacts: []
        }
      }
      
      const emailsSent = result.emails_sent || 0
      const emailsAttempted = result.emails_attempted || emailCount
      const isDemo = result.demo_mode || false
      
      // Track campaign success with metrics
      const totalCampaignDuration = Date.now() - campaignStartTime
      await this.metricsService.trackAgentAction({
        agent_name: 'coordinator',
        action_type: emailsSent > 0 ? 'email_sent' : 'email_failed',
        campaign_id: campaignId,
        success: emailsSent > 0,
        duration_ms: totalCampaignDuration,
        metadata: {
          backend_powered: true,
          demo_mode: isDemo,
          emails_sent: emailsSent,
          emails_attempted: emailsAttempted,
          success_rate: emailsAttempted > 0 ? (emailsSent / emailsAttempted) * 100 : 0
        }
      })
      
      const demoIndicator = isDemo ? ' 🧪 (Demo Mode)' : ''
      return {
        success: true,
        message: `✅ Campaign completed! Successfully sent ${emailsSent} emails${demoIndicator}`,
        emailsSent: emailsSent,
        errors: [],
        selectedContacts: result.results || []  // Demo returns contact details
      }
      
    } catch (error) {
      console.error('Campaign failed:', error)
      
      // Track failure
      await this.metricsService.trackAgentAction({
        agent_name: 'coordinator',
        action_type: 'email_failed',
        campaign_id: campaignId,
        success: false,
        duration_ms: Date.now() - campaignStartTime,
        error_message: error instanceof Error ? error.message : 'Unknown error',
        metadata: {}
      })
      
      return {
        success: false,
        message: `❌ Campaign failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        emailsSent: 0,
        errors: [error instanceof Error ? error.message : 'Unknown error'],
        selectedContacts: []
      }
    }
  }
  
  private async getContactsForCampaign(limitCount: number): Promise<Contact[]> {
    try {
      const contactsRef = collection(db, 'healthcare_contacts')
      console.log('🔍 Searching for contacts in Firestore...')
      
      // First, try to get any contacts without qualification_score filter to see what's available
      let q = query(
        contactsRef,
        limit(limitCount * 3) // Get more than needed for filtering
      )
      
      const querySnapshot = await getDocs(q)
      console.log(`📊 Found ${querySnapshot.size} total contacts in database`)
      
      const allContacts: Contact[] = []
      const thirtyDaysAgo = new Date()
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
      
      querySnapshot.forEach((doc) => {
        const data = doc.data()
        allContacts.push({
          id: doc.id,
          ...data
        } as Contact)
      })
      
      console.log('📋 Sample contact structure:', allContacts[0])
      
      // Filter contacts based on availability and basic criteria
      const availableContacts = allContacts.filter(contact => {
        const hasEmail = !!contact.email
        const lastContacted = contact.last_contacted?.toDate()
        const recentlyContacted = lastContacted && lastContacted > thirtyDaysAgo
        
        // More flexible qualification - use any contact with email that hasn't been contacted recently
        const qualificationScore = contact.qualification_score || 5 // Default score if missing
        const isQualified = qualificationScore >= 5 // Lower threshold
        
        return hasEmail && !recentlyContacted && isQualified
      })
      
      console.log(`✅ Found ${availableContacts.length} available contacts after filtering`)
      
      // Sort by qualification score if available, otherwise by company name
      availableContacts.sort((a, b) => {
        const scoreA = a.qualification_score || 5
        const scoreB = b.qualification_score || 5
        return scoreB - scoreA // Highest score first
      })
      
      const selectedContacts = availableContacts.slice(0, limitCount)
      console.log(`🎯 Selected ${selectedContacts.length} contacts for campaign`)
      
      return selectedContacts
    } catch (error) {
      console.error('Error getting contacts for campaign:', error)
      
      // Fallback: try a simpler query without complex filters
      try {
        console.log('🔄 Attempting fallback query...')
        const simpleQuery = query(collection(db, 'healthcare_contacts'), limit(limitCount))
        const fallbackSnapshot = await getDocs(simpleQuery)
        const fallbackContacts: Contact[] = []
        
        fallbackSnapshot.forEach((doc) => {
          const data = doc.data()
          if (data.email) { // Only require email
            fallbackContacts.push({
              id: doc.id,
              ...data
            } as Contact)
          }
        })
        
        console.log(`🔄 Fallback found ${fallbackContacts.length} contacts with emails`)
        return fallbackContacts
      } catch (fallbackError) {
        console.error('Fallback query also failed:', fallbackError)
        return []
      }
    }
  }
  
  private async processContactsCampaign(contacts: Contact[], campaignId: string): Promise<{success: boolean, error?: string}[]> {
    const results: {success: boolean, error?: string}[] = []
    
    for (const contact of contacts) {
      const contactStartTime = Date.now()
      
      try {
        // Step 1: Qualification Agent - Re-validate contact eligibility
        const qualificationStartTime = Date.now()
        const isQualified = await this.validateContactQualification(contact)
        const qualificationDuration = Date.now() - qualificationStartTime
        
        await this.metricsService.trackLeadQualification(
          contact.id, 
          contact.qualification_score || 0, 
          qualificationDuration, 
          isQualified
        )
        
        if (!isQualified) {
          results.push({ success: false, error: 'Contact no longer qualified' })
          continue
        }
        
        // Step 2: Email Composer Agent - Generate personalized content
        const emailComposerStartTime = Date.now()
        const emailContent = await this.generatePersonalizedEmail(contact)
        const emailComposerDuration = Date.now() - emailComposerStartTime
        
        await this.metricsService.trackAgentAction({
          agent_name: 'email_composer',
          action_type: 'email_sent',
          contact_id: contact.id,
          campaign_id: campaignId,
          success: true,
          duration_ms: emailComposerDuration,
          metadata: {
            subject_length: emailContent.subject.length,
            body_length: emailContent.body.length,
            personalization_score: this.calculatePersonalizationScore(emailContent, contact)
          }
        })
        
        // Step 3: Create email campaign record
        const campaignRecord = {
          contact_id: contact.id,
          subject: emailContent.subject,
          body: emailContent.body,
          sent_at: Timestamp.now(),
          status: 'sent' as const,
          campaign_type: 'frontend_automated',
          campaign_id: campaignId
        }
        
        // Step 4: Save to email_campaigns collection
        await addDoc(collection(db, 'email_campaigns'), campaignRecord)
        
        // Step 5: Update contact's last_contacted timestamp
        const contactRef = doc(db, 'healthcare_contacts', contact.id)
        await updateDoc(contactRef, {
          last_contacted: Timestamp.now(),
          email_sent_count: (contact.email_sent_count || 0) + 1
        })
        
        // Step 6: Track successful email sent
        const totalContactDuration = Date.now() - contactStartTime
        await this.metricsService.trackEmailSent(
          'email_composer', 
          contact.id, 
          campaignId, 
          totalContactDuration, 
          true
        )
        
        console.log(`✅ Email campaign record created for ${contact.contact_name} (${totalContactDuration}ms)`)
        results.push({ success: true })
        
        // Add small delay between processing contacts
        await this.delay(200)
        
      } catch (error) {
        const errorDuration = Date.now() - contactStartTime
        
        // Track failed email attempt
        await this.metricsService.trackEmailSent(
          'email_composer', 
          contact.id, 
          campaignId, 
          errorDuration, 
          false,
          error instanceof Error ? error.message : 'Processing failed'
        )
        
        console.error(`❌ Failed to process ${contact.contact_name}:`, error)
        results.push({ 
          success: false, 
          error: error instanceof Error ? error.message : 'Processing failed' 
        })
      }
    }
    
    return results
  }
  
  private async generatePersonalizedEmail(contact: Contact): Promise<{subject: string, body: string}> {
    // Simulate AI-generated personalized content
    // In production, this would call your AI service
    
    const subjects = [
      `Partnership Opportunity for ${contact.company_name}`,
      `Medical Device Solutions for ${contact.company_name}`,
      `Enhancing Patient Care at ${contact.company_name}`,
      `Innovation Partnership with GFMD`,
      `Advanced Medical Technology for ${contact.company_name}`
    ]
    
    const subject = subjects[Math.floor(Math.random() * subjects.length)]
    
    const body = `Dear ${contact.contact_name || 'Healthcare Professional'},

I hope this message finds you well. My name is Sarah from GFMD Medical Solutions, and I'm reaching out because of your role as ${contact.title || 'a healthcare leader'} at ${contact.company_name}.

We've been working with leading healthcare facilities to implement cutting-edge medical device solutions that have resulted in:
• 25% reduction in patient wait times
• 40% improvement in diagnostic accuracy
• Significant cost savings on equipment maintenance

Given ${contact.company_name}'s commitment to excellence in patient care, I believe our solutions could provide tremendous value to your organization.

Would you be available for a brief 15-minute call next week to discuss how we might support ${contact.company_name}'s goals?

Best regards,
Sarah Mitchell
Senior Healthcare Solutions Consultant
GFMD Medical Solutions
📧 sarah.mitchell@gfmd.com
📱 (555) 123-4567

P.S. I've included a case study showing how we helped a similar ${contact.facility_type || 'healthcare facility'} achieve remarkable results. I'd be happy to discuss how this could apply to your specific situation.`

    return { subject, body }
  }
  
  private async validateContactQualification(contact: Contact): Promise<boolean> {
    // More lenient qualification validation to ensure we can process contacts
    const score = contact.qualification_score || 5 // Default to 5 if no score
    const hasEmail = !!contact.email
    const hasName = !!contact.contact_name
    
    // Check if contacted recently (30 days)
    const recentlyContacted = contact.last_contacted && 
      (new Date().getTime() - contact.last_contacted.toDate().getTime()) < (30 * 24 * 60 * 60 * 1000)
    
    // More lenient criteria: just need email, name, and not recently contacted
    const isValid = hasEmail && hasName && !recentlyContacted
    
    console.log(`🔍 Validating contact ${contact.contact_name}: score=${score}, email=${hasEmail}, name=${hasName}, recentlyContacted=${recentlyContacted}, valid=${isValid}`)
    
    return isValid
  }
  
  private calculatePersonalizationScore(emailContent: { subject: string, body: string }, contact: Contact): number {
    let score = 0
    
    // Check if contact name is used
    if (contact.contact_name && emailContent.body.includes(contact.contact_name)) score += 20
    
    // Check if company name is used  
    if (contact.company_name && emailContent.body.includes(contact.company_name)) score += 20
    
    // Check if title is referenced
    if (contact.title && emailContent.body.includes(contact.title)) score += 15
    
    // Check if facility type is referenced
    if (contact.facility_type && emailContent.body.includes(contact.facility_type)) score += 15
    
    // Check if location is referenced
    if (contact.city && emailContent.body.includes(contact.city)) score += 10
    if (contact.state && emailContent.body.includes(contact.state)) score += 10
    
    // Bonus for longer, more detailed content
    if (emailContent.body.length > 500) score += 10
    
    return Math.min(score, 100) // Cap at 100
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
  
  async getCampaignPreview(emailCount: number): Promise<{
    availableContacts: number
    selectedContacts: Contact[]
    estimatedDuration: string
  }> {
    const contacts = await this.getContactsForCampaign(emailCount)
    
    return {
      availableContacts: contacts.length,
      selectedContacts: contacts,
      estimatedDuration: `${Math.ceil(contacts.length * 0.2)} seconds`
    }
  }
  
  async debugDatabaseStatus(): Promise<{
    totalContacts: number
    contactsWithEmails: number
    contactsWithNames: number
    contactsWithScores: number
    recentlyContacted: number
    sampleContacts: any[]
  }> {
    try {
      const contactsRef = collection(db, 'healthcare_contacts')
      const allContactsQuery = query(contactsRef, limit(1000)) // Check first 1000
      const snapshot = await getDocs(allContactsQuery)
      
      let contactsWithEmails = 0
      let contactsWithNames = 0  
      let contactsWithScores = 0
      let recentlyContacted = 0
      const sampleContacts: any[] = []
      
      const thirtyDaysAgo = new Date()
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
      
      let index = 0;
      snapshot.forEach((doc) => {
        const data = doc.data()
        
        if (data.email) contactsWithEmails++
        if (data.contact_name) contactsWithNames++
        if (data.qualification_score) contactsWithScores++
        if (data.last_contacted && data.last_contacted.toDate() > thirtyDaysAgo) recentlyContacted++
        
        // Collect first 3 contacts as samples
        if (index < 3) {
          sampleContacts.push({
            id: doc.id,
            contact_name: data.contact_name,
            email: data.email,
            company_name: data.company_name,
            qualification_score: data.qualification_score,
            last_contacted: data.last_contacted ? data.last_contacted.toDate().toISOString() : null
          })
        }
      })
      
      return {
        totalContacts: snapshot.size,
        contactsWithEmails,
        contactsWithNames,
        contactsWithScores,
        recentlyContacted,
        sampleContacts
      }
    } catch (error) {
      console.error('Error debugging database:', error)
      return {
        totalContacts: 0,
        contactsWithEmails: 0,
        contactsWithNames: 0,
        contactsWithScores: 0,
        recentlyContacted: 0,
        sampleContacts: []
      }
    }
  }
}