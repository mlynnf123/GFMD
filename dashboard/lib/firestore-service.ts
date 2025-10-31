import { 
  collection, 
  query, 
  where, 
  orderBy, 
  limit, 
  getDocs, 
  doc, 
  getDoc,
  onSnapshot,
  Timestamp
} from 'firebase/firestore'
import { db } from './firebase'

export interface Contact {
  id: string
  contact_name: string
  email: string
  company_name: string
  title: string
  city: string
  state: string
  phone?: string
  qualification_score?: number
  last_contacted?: Timestamp
  email_sent_count?: number
  facility_type?: string
  research_status?: string
}

export interface EmailCampaign {
  id: string
  contact_id: string
  subject: string
  body: string
  sent_at: Timestamp
  status: 'sent' | 'failed' | 'pending'
  message_id?: string
  campaign_type?: string
}

export interface SystemStats {
  date: string
  emails_sent: number
  emails_failed: number
  contacts_processed: number
  qualification_scores: number[]
}

export class FirestoreService {
  
  // Get contacts for outreach (not contacted recently)
  async getContactsForOutreach(limitCount: number = 50): Promise<Contact[]> {
    try {
      const contactsRef = collection(db, 'healthcare_contacts')
      
      // Get contacts that haven't been contacted in the last 30 days or never contacted
      const thirtyDaysAgo = new Date()
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
      
      const q = query(
        contactsRef,
        where('qualification_score', '>=', 7),
        orderBy('qualification_score', 'desc'),
        limit(limitCount)
      )
      
      const querySnapshot = await getDocs(q)
      const contacts: Contact[] = []
      
      querySnapshot.forEach((doc) => {
        const data = doc.data()
        const lastContacted = data.last_contacted?.toDate()
        
        // Only include if never contacted or contacted more than 30 days ago
        if (!lastContacted || lastContacted < thirtyDaysAgo) {
          contacts.push({
            id: doc.id,
            ...data
          } as Contact)
        }
      })
      
      return contacts
    } catch (error) {
      console.error('Error getting contacts for outreach:', error)
      return []
    }
  }

  // Get total contact statistics
  async getContactStats(): Promise<{
    total: number
    qualified: number
    neverContacted: number
    avgQualificationScore: number
  }> {
    try {
      const contactsRef = collection(db, 'healthcare_contacts')
      const allContactsQuery = query(contactsRef)
      const qualifiedQuery = query(contactsRef, where('qualification_score', '>=', 7))
      
      const [allSnapshot, qualifiedSnapshot] = await Promise.all([
        getDocs(allContactsQuery),
        getDocs(qualifiedQuery)
      ])
      
      let neverContacted = 0
      let totalQualificationScore = 0
      let qualifiedContacts = 0
      
      allSnapshot.forEach((doc) => {
        const data = doc.data()
        if (!data.last_contacted) {
          neverContacted++
        }
        if (data.qualification_score) {
          totalQualificationScore += data.qualification_score
          qualifiedContacts++
        }
      })
      
      return {
        total: allSnapshot.size,
        qualified: qualifiedSnapshot.size,
        neverContacted,
        avgQualificationScore: qualifiedContacts > 0 ? totalQualificationScore / qualifiedContacts : 0
      }
    } catch (error) {
      console.error('Error getting contact stats:', error)
      return { total: 0, qualified: 0, neverContacted: 0, avgQualificationScore: 0 }
    }
  }

  // Get email campaign statistics
  async getEmailStats(days: number = 30): Promise<{
    totalSent: number
    successRate: number
    dailyStats: { date: string; sent: number; success: number }[]
  }> {
    try {
      const emailsRef = collection(db, 'email_campaigns')
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - days)
      
      const q = query(
        emailsRef,
        where('sent_at', '>=', Timestamp.fromDate(startDate)),
        orderBy('sent_at', 'desc')
      )
      
      const querySnapshot = await getDocs(q)
      const emailsByDate: { [key: string]: { sent: number; success: number } } = {}
      let totalSent = 0
      let totalSuccess = 0
      
      querySnapshot.forEach((doc) => {
        const data = doc.data()
        const date = data.sent_at.toDate().toISOString().split('T')[0]
        
        if (!emailsByDate[date]) {
          emailsByDate[date] = { sent: 0, success: 0 }
        }
        
        emailsByDate[date].sent++
        totalSent++
        
        if (data.status === 'sent') {
          emailsByDate[date].success++
          totalSuccess++
        }
      })
      
      const dailyStats = Object.entries(emailsByDate).map(([date, stats]) => ({
        date,
        ...stats
      }))
      
      return {
        totalSent,
        successRate: totalSent > 0 ? (totalSuccess / totalSent) * 100 : 0,
        dailyStats
      }
    } catch (error) {
      console.error('Error getting email stats:', error)
      return { totalSent: 0, successRate: 0, dailyStats: [] }
    }
  }

  // Get recent email campaigns
  async getRecentEmails(limitCount: number = 10): Promise<(EmailCampaign & { contact?: Contact })[]> {
    try {
      const emailsRef = collection(db, 'email_campaigns')
      const q = query(
        emailsRef,
        orderBy('sent_at', 'desc'),
        limit(limitCount)
      )
      
      const querySnapshot = await getDocs(q)
      const emails: (EmailCampaign & { contact?: Contact })[] = []
      
      for (const emailDoc of querySnapshot.docs) {
        const emailData = emailDoc.data() as EmailCampaign
        
        // Get contact information
        if (emailData.contact_id) {
          const contactDoc = await getDoc(doc(db, 'healthcare_contacts', emailData.contact_id))
          if (contactDoc.exists()) {
            emails.push({
              id: emailDoc.id,
              ...emailData,
              contact: { id: contactDoc.id, ...contactDoc.data() } as Contact
            })
          }
        }
      }
      
      return emails
    } catch (error) {
      console.error('Error getting recent emails:', error)
      return []
    }
  }

  // Real-time subscription for dashboard updates
  subscribeToStats(callback: (stats: any) => void) {
    const emailsRef = collection(db, 'email_campaigns')
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    const q = query(
      emailsRef,
      where('sent_at', '>=', Timestamp.fromDate(today))
    )
    
    return onSnapshot(q, (snapshot) => {
      let emailsSent = 0
      let emailsSuccess = 0
      
      snapshot.forEach((doc) => {
        const data = doc.data()
        emailsSent++
        if (data.status === 'sent') {
          emailsSuccess++
        }
      })
      
      callback({
        dailyEmailsSent: emailsSent,
        dailySuccessRate: emailsSent > 0 ? (emailsSuccess / emailsSent) * 100 : 0,
        emailsRemaining: Math.max(0, 100 - emailsSent) // Assuming 100 daily limit
      })
    })
  }
}