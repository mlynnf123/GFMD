import { 
  collection, 
  doc,
  getDoc,
  deleteDoc,
  updateDoc,
  query,
  where,
  getDocs,
  addDoc,
  Timestamp,
  orderBy,
  limit
} from 'firebase/firestore'
import { db } from './firebase'
import { AgentMetricsService } from './agent-metrics-service'

export interface EmailDeliveryStatus {
  campaign_id: string
  contact_id: string
  email: string
  status: 'sent' | 'delivered' | 'bounced' | 'failed' | 'unsubscribed' | 'spam_complaint'
  error_message?: string
  bounce_type?: 'soft' | 'hard' | 'spam' | 'invalid'
  timestamp: Timestamp
  retry_count: number
  should_remove_contact: boolean
}

export interface MonitoringResult {
  checked: number
  removed: number
  updated: number
  errors: string[]
}

export class EmailMonitoringService {
  private metricsService = new AgentMetricsService()
  
  async trackEmailDeliveryStatus(
    campaignId: string,
    contactId: string,
    email: string,
    status: EmailDeliveryStatus['status'],
    errorMessage?: string,
    bounceType?: EmailDeliveryStatus['bounce_type']
  ): Promise<void> {
    try {
      const shouldRemove = this.shouldRemoveContact(status, bounceType)
      
      const deliveryRecord: EmailDeliveryStatus = {
        campaign_id: campaignId,
        contact_id: contactId,
        email: email.toLowerCase(),
        status,
        error_message: errorMessage,
        bounce_type: bounceType,
        timestamp: Timestamp.now(),
        retry_count: 0,
        should_remove_contact: shouldRemove
      }
      
      // Save delivery status to tracking collection
      await addDoc(collection(db, 'email_delivery_tracking'), deliveryRecord)
      
      // Track metrics
      await this.metricsService.trackAgentAction({
        agent_name: 'coordinator',
        action_type: status === 'delivered' || status === 'sent' ? 'email_sent' : 'email_failed',
        contact_id: contactId,
        campaign_id: campaignId,
        success: status === 'delivered' || status === 'sent',
        duration_ms: 1000,
        metadata: {
          email_status: status,
          bounce_type: bounceType || 'none',
          should_remove: shouldRemove
        },
        error_message: errorMessage
      })
      
      // If contact should be removed, mark for cleanup
      if (shouldRemove) {
        await this.markContactForRemoval(contactId, email, status, bounceType, errorMessage)
      }
      
      console.log(`📧 Tracked email delivery: ${email} - ${status} (remove: ${shouldRemove})`)
      
    } catch (error) {
      console.error('Error tracking email delivery:', error)
    }
  }
  
  private shouldRemoveContact(
    status: EmailDeliveryStatus['status'], 
    bounceType?: EmailDeliveryStatus['bounce_type']
  ): boolean {
    // Remove contacts for hard bounces and permanent failures
    if (status === 'bounced' && bounceType === 'hard') return true
    if (status === 'bounced' && bounceType === 'invalid') return true
    if (status === 'failed' && bounceType === 'invalid') return true
    
    // Remove spam complaints (they opted out)
    if (status === 'spam_complaint') return true
    
    // Remove unsubscribes
    if (status === 'unsubscribed') return true
    
    return false
  }
  
  private async markContactForRemoval(
    contactId: string,
    email: string,
    status: EmailDeliveryStatus['status'],
    bounceType?: EmailDeliveryStatus['bounce_type'],
    errorMessage?: string
  ): Promise<void> {
    try {
      const removalRecord = {
        contact_id: contactId,
        email: email.toLowerCase(),
        removal_reason: status,
        bounce_type: bounceType || 'unknown',
        error_message: errorMessage || '',
        marked_for_removal_at: Timestamp.now(),
        removed: false,
        removal_processed_at: null
      }
      
      await addDoc(collection(db, 'contacts_marked_for_removal'), removalRecord)
      console.log(`🗑️ Marked contact ${contactId} (${email}) for removal: ${status}`)
      
    } catch (error) {
      console.error('Error marking contact for removal:', error)
    }
  }
  
  async processContactRemovals(): Promise<MonitoringResult> {
    const result: MonitoringResult = {
      checked: 0,
      removed: 0,
      updated: 0,
      errors: []
    }
    
    try {
      // Get contacts marked for removal
      const markedQuery = query(
        collection(db, 'contacts_marked_for_removal'),
        where('removed', '==', false),
        orderBy('marked_for_removal_at', 'desc'),
        limit(100) // Process in batches
      )
      
      const markedSnapshot = await getDocs(markedQuery)
      result.checked = markedSnapshot.size
      
      console.log(`🔍 Processing ${result.checked} contacts marked for removal...`)
      
      for (const markedDoc of markedSnapshot.docs) {
        try {
          const markedData = markedDoc.data()
          const contactId = markedData.contact_id
          
          // Check if contact still exists
          const contactRef = doc(db, 'healthcare_contacts', contactId)
          const contactDoc = await getDoc(contactRef)
          
          if (contactDoc.exists()) {
            // Remove the contact
            await deleteDoc(contactRef)
            
            // Update the removal record
            await updateDoc(doc(db, 'contacts_marked_for_removal', markedDoc.id), {
              removed: true,
              removal_processed_at: Timestamp.now()
            })
            
            result.removed++
            console.log(`🗑️ Removed contact ${contactId}: ${markedData.email} (${markedData.removal_reason})`)
            
            // Track the removal
            await this.metricsService.trackAgentAction({
              agent_name: 'coordinator',
              action_type: 'email_failed',
              contact_id: contactId,
              success: false,
              duration_ms: 500,
              metadata: {
                action: 'contact_removed',
                removal_reason: markedData.removal_reason,
                bounce_type: markedData.bounce_type
              },
              error_message: `Contact removed due to ${markedData.removal_reason}`
            })
            
          } else {
            // Contact already doesn't exist, mark as processed
            await updateDoc(doc(db, 'contacts_marked_for_removal', markedDoc.id), {
              removed: true,
              removal_processed_at: Timestamp.now()
            })
            result.updated++
          }
          
        } catch (error) {
          result.errors.push(`Error processing contact ${markedDoc.id}: ${error instanceof Error ? error.message : 'Unknown error'}`)
          console.error(`Error processing marked contact:`, error)
        }
      }
      
      console.log(`✅ Removal processing complete: ${result.removed} removed, ${result.updated} updated`)
      
    } catch (error) {
      result.errors.push(`Removal process failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      console.error('Error in contact removal process:', error)
    }
    
    return result
  }
  
  async simulateEmailBounces(): Promise<void> {
    // For testing - simulate some email bounces
    console.log('🧪 Simulating email bounces for testing...')
    
    try {
      const contactsQuery = query(
        collection(db, 'healthcare_contacts'),
        limit(3)
      )
      
      const contactsSnapshot = await getDocs(contactsQuery)
      
      for (const contactDoc of contactsSnapshot.docs) {
        const contactData = contactDoc.data()
        
        // Simulate different bounce types
        const bounceTypes: { status: EmailDeliveryStatus['status'], bounceType?: EmailDeliveryStatus['bounce_type'], error: string }[] = [
          { status: 'bounced', bounceType: 'hard', error: 'Email address does not exist' },
          { status: 'bounced', bounceType: 'invalid', error: 'Invalid email format' },
          { status: 'delivered', error: '' } // Some successful ones
        ]
        
        const bounce = bounceTypes[Math.floor(Math.random() * bounceTypes.length)]
        
        await this.trackEmailDeliveryStatus(
          'test_campaign_' + Date.now(),
          contactDoc.id,
          contactData.email || 'test@example.com',
          bounce.status,
          bounce.error,
          bounce.bounceType
        )
      }
      
      console.log('✅ Email bounce simulation complete')
      
    } catch (error) {
      console.error('Error simulating bounces:', error)
    }
  }
  
  async getDeliveryStats(days: number = 7): Promise<{
    totalEmails: number
    delivered: number
    bounced: number
    failed: number
    hardBounces: number
    contactsRemoved: number
    deliveryRate: number
  }> {
    try {
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)
      
      const deliveryQuery = query(
        collection(db, 'email_delivery_tracking'),
        where('timestamp', '>=', Timestamp.fromDate(startDate))
      )
      
      const deliverySnapshot = await getDocs(deliveryQuery)
      
      let totalEmails = 0
      let delivered = 0
      let bounced = 0
      let failed = 0
      let hardBounces = 0
      let contactsRemoved = 0
      
      deliverySnapshot.forEach((doc) => {
        const data = doc.data()
        totalEmails++
        
        switch (data.status) {
          case 'delivered':
          case 'sent':
            delivered++
            break
          case 'bounced':
            bounced++
            if (data.bounce_type === 'hard') hardBounces++
            break
          case 'failed':
            failed++
            break
        }
        
        if (data.should_remove_contact) contactsRemoved++
      })
      
      const deliveryRate = totalEmails > 0 ? (delivered / totalEmails) * 100 : 0
      
      return {
        totalEmails,
        delivered,
        bounced,
        failed,
        hardBounces,
        contactsRemoved,
        deliveryRate
      }
      
    } catch (error) {
      console.error('Error getting delivery stats:', error)
      return {
        totalEmails: 0,
        delivered: 0,
        bounced: 0,
        failed: 0,
        hardBounces: 0,
        contactsRemoved: 0,
        deliveryRate: 0
      }
    }
  }
  
  async scheduleAutomaticCleanup(): Promise<void> {
    console.log('🔄 Starting automatic email monitoring and cleanup...')
    
    // Process removals every 5 minutes
    setInterval(async () => {
      try {
        const result = await this.processContactRemovals()
        if (result.removed > 0 || result.errors.length > 0) {
          console.log('🧹 Cleanup result:', result)
        }
      } catch (error) {
        console.error('Error in scheduled cleanup:', error)
      }
    }, 5 * 60 * 1000) // 5 minutes
    
    console.log('✅ Automatic cleanup scheduled (runs every 5 minutes)')
  }
}