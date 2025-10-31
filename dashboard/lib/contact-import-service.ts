import { 
  collection, 
  doc,
  setDoc,
  getDoc,
  query,
  where,
  getDocs,
  addDoc,
  Timestamp 
} from 'firebase/firestore'
import { db } from './firebase'

export interface ImportContact {
  definitive_executive_id: string
  executive_name: string
  title: string
  standardized_title: string
  business_email: string
  office_phone: string
  organization_phone: string
  definitive_id: string
  hospital_name: string
  firm_type: string
  hospital_type: string
  address: string
  address1: string
  city: string
  state: string
  region: string
  // FullEnrich fields
  first_name?: string
  last_name?: string
  linkedin_url?: string
  company_name?: string
  fullenrich_email?: string
  bounce_status?: string
  all_valid_emails?: string
  all_probably_valid_emails?: string
  row_status?: string
  linkedin_url_fullenrich?: string
}

export interface ImportResult {
  processed: number
  added: number
  duplicates: number
  errors: number
  errorMessages: string[]
}

export class ContactImportService {
  
  async importContactsFromCSV(csvContent: string): Promise<ImportResult> {
    const result: ImportResult = {
      processed: 0,
      added: 0,
      duplicates: 0,
      errors: 0,
      errorMessages: []
    }
    
    try {
      // Parse CSV content
      const lines = csvContent.split('\n')
      const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, '').replace(/﻿/g, ''))
      
      console.log('📋 CSV Headers:', headers)
      console.log(`📊 Found ${lines.length - 1} contact records to process`)
      
      // Detect CSV format
      const csvFormat = this.detectCSVFormat(headers)
      console.log(`🔍 Detected CSV format: ${csvFormat}`)
      
      // Process each line (skip header)
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim()
        if (!line) continue // Skip empty lines
        
        try {
          result.processed++
          const values = this.parseCSVLine(line)
          
          if (values.length < headers.length - 1) {
            console.warn(`⚠️ Line ${i + 1}: Insufficient columns (${values.length}/${headers.length})`)
            continue
          }
          
          // Map CSV data to contact object based on format
          const contact = this.mapCSVToContact(headers, values, csvFormat)
          
          // Get the best email (prefer FullEnrich verified emails)
          const bestEmail = this.getBestEmail(contact)
          const contactName = contact.executive_name || `${contact.first_name || ''} ${contact.last_name || ''}`.trim()
          
          if (!bestEmail || !contactName) {
            console.log(`⏭️ Skipping contact ${contactName || 'Unknown'}: Missing email or name`)
            continue
          }
          
          // Check for duplicates
          const isDuplicate = await this.checkForDuplicate(contact)
          
          if (isDuplicate) {
            result.duplicates++
            console.log(`🔄 Duplicate found: ${contact.executive_name} (${contact.business_email})`)
            continue
          }
          
          // Add to Firestore
          await this.addContactToFirestore(contact)
          result.added++
          
          console.log(`✅ Added: ${contact.executive_name} at ${contact.hospital_name}`)
          
          // Add small delay to avoid overwhelming Firestore
          if (result.processed % 50 === 0) {
            console.log(`📊 Progress: ${result.processed} processed, ${result.added} added, ${result.duplicates} duplicates`)
            await this.delay(100)
          }
          
        } catch (error) {
          result.errors++
          const errorMsg = `Line ${i + 1}: ${error instanceof Error ? error.message : 'Unknown error'}`
          result.errorMessages.push(errorMsg)
          console.error(`❌ Error processing line ${i + 1}:`, error)
        }
      }
      
      console.log(`🎉 Import completed! Processed: ${result.processed}, Added: ${result.added}, Duplicates: ${result.duplicates}, Errors: ${result.errors}`)
      
    } catch (error) {
      result.errors++
      result.errorMessages.push(`Import failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      console.error('❌ Import failed:', error)
    }
    
    return result
  }
  
  private parseCSVLine(line: string): string[] {
    const values: string[] = []
    let current = ''
    let inQuotes = false
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i]
      
      if (char === '"') {
        inQuotes = !inQuotes
      } else if (char === ',' && !inQuotes) {
        values.push(current.trim())
        current = ''
      } else {
        current += char
      }
    }
    
    values.push(current.trim())
    return values
  }
  
  private detectCSVFormat(headers: string[]): 'definitive' | 'fullenrich' {
    // Check for FullEnrich specific columns
    const hasFullEnrichColumns = headers.some(header => 
      header.toLowerCase().includes('fullenrich') || 
      header.toLowerCase().includes('bounce status') ||
      header.toLowerCase().includes('linkedin url')
    )
    
    return hasFullEnrichColumns ? 'fullenrich' : 'definitive'
  }
  
  private getBestEmail(contact: ImportContact): string {
    // For FullEnrich format, prefer verified emails
    if (contact.fullenrich_email && contact.bounce_status === 'Valid & safe to send email') {
      return contact.fullenrich_email.toLowerCase()
    }
    
    if (contact.all_valid_emails) {
      return contact.all_valid_emails.split(',')[0].trim().toLowerCase()
    }
    
    if (contact.all_probably_valid_emails) {
      return contact.all_probably_valid_emails.split(',')[0].trim().toLowerCase()
    }
    
    // Fall back to business email
    if (contact.business_email) {
      return contact.business_email.toLowerCase()
    }
    
    if (contact.fullenrich_email) {
      return contact.fullenrich_email.toLowerCase()
    }
    
    return ''
  }

  private mapCSVToContact(headers: string[], values: string[], format: 'definitive' | 'fullenrich'): ImportContact {
    const contact: any = {}
    
    headers.forEach((header, index) => {
      const key = header.toLowerCase().replace(/ /g, '_')
      contact[key] = values[index] ? values[index].replace(/"/g, '').trim() : ''
    })
    
    return contact as ImportContact
  }
  
  private async checkForDuplicate(contact: ImportContact): Promise<boolean> {
    try {
      // Check by email first (most reliable)
      if (contact.business_email) {
        const emailQuery = query(
          collection(db, 'healthcare_contacts'),
          where('email', '==', contact.business_email.toLowerCase())
        )
        const emailSnapshot = await getDocs(emailQuery)
        if (!emailSnapshot.empty) {
          return true
        }
      }
      
      // Check by definitive_executive_id if available
      if (contact.definitive_executive_id) {
        const idQuery = query(
          collection(db, 'healthcare_contacts'),
          where('definitive_executive_id', '==', contact.definitive_executive_id)
        )
        const idSnapshot = await getDocs(idQuery)
        if (!idSnapshot.empty) {
          return true
        }
      }
      
      return false
    } catch (error) {
      console.error('Error checking for duplicate:', error)
      return false // If check fails, proceed with add
    }
  }
  
  private async addContactToFirestore(contact: ImportContact): Promise<void> {
    const bestEmail = this.getBestEmail(contact)
    const contactName = contact.executive_name || `${contact.first_name || ''} ${contact.last_name || ''}`.trim()
    
    const firestoreContact = {
      // Map CSV fields to Firestore schema
      definitive_executive_id: contact.definitive_executive_id || '',
      contact_name: contactName,
      email: bestEmail,
      title: contact.title || '',
      standardized_title: contact.standardized_title || '',
      phone: contact.office_phone || contact.organization_phone || '',
      company_name: contact.hospital_name || '',
      facility_type: contact.hospital_type || contact.firm_type || 'Healthcare',
      address: contact.address || contact.address1 || '',
      city: contact.city || '',
      state: contact.state || '',
      region: contact.region || '',
      
      // Set default qualification score based on title
      qualification_score: this.calculateQualificationScore(contact),
      
      // Import metadata
      imported_at: Timestamp.now(),
      data_source: contact.bounce_status ? 'fullenrich_csv' : 'definitive_healthcare_csv',
      definitive_id: contact.definitive_id || '',
      
      // FullEnrich metadata if available
      ...(contact.bounce_status && {
        fullenrich_bounce_status: contact.bounce_status,
        linkedin_url: contact.linkedin_url || contact.linkedin_url_fullenrich || '',
        email_validation_status: contact.bounce_status,
        all_emails: contact.all_valid_emails || contact.all_probably_valid_emails || ''
      }),
      
      // Campaign tracking fields
      email_sent_count: 0,
      last_contacted: null,
      research_status: 'imported'
    }
    
    // Use definitive_executive_id as document ID if available, otherwise auto-generate
    if (contact.definitive_executive_id) {
      await setDoc(doc(db, 'healthcare_contacts', contact.definitive_executive_id), firestoreContact)
    } else {
      await addDoc(collection(db, 'healthcare_contacts'), firestoreContact)
    }
  }
  
  private calculateQualificationScore(contact: ImportContact): number {
    let score = 5 // Base score
    
    // Title-based scoring
    const title = (contact.title || '').toLowerCase()
    const standardizedTitle = (contact.standardized_title || '').toLowerCase()
    
    if (title.includes('director') || title.includes('manager')) score += 2
    if (title.includes('chief') || title.includes('vp') || title.includes('vice president')) score += 3
    if (title.includes('medical director') || title.includes('lab director')) score += 2
    if (standardizedTitle.includes('laboratory')) score += 1
    
    // Hospital type scoring
    const hospitalType = (contact.hospital_type || '').toLowerCase()
    if (hospitalType.includes('acute care')) score += 1
    if (hospitalType.includes('critical access')) score += 1
    
    // Firm type scoring  
    const firmType = (contact.firm_type || '').toLowerCase()
    if (firmType === 'hospital') score += 1
    if (firmType === 'health system') score += 2
    
    // Email quality scoring
    if (contact.business_email && contact.business_email.includes('@')) {
      score += 1
      // Bonus for institutional emails
      if (!contact.business_email.includes('gmail') && 
          !contact.business_email.includes('yahoo') && 
          !contact.business_email.includes('hotmail')) {
        score += 1
      }
    }
    
    return Math.min(Math.max(score, 1), 10) // Clamp between 1-10
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
  
  async getImportStats(): Promise<{
    totalContacts: number
    importedToday: number
    byDataSource: { [key: string]: number }
  }> {
    try {
      const contactsRef = collection(db, 'healthcare_contacts')
      const allContactsSnapshot = await getDocs(contactsRef)
      
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      let importedToday = 0
      const byDataSource: { [key: string]: number } = {}
      
      allContactsSnapshot.forEach((doc) => {
        const data = doc.data()
        
        // Count imports today
        if (data.imported_at && data.imported_at.toDate() >= today) {
          importedToday++
        }
        
        // Count by data source
        const source = data.data_source || 'unknown'
        byDataSource[source] = (byDataSource[source] || 0) + 1
      })
      
      return {
        totalContacts: allContactsSnapshot.size,
        importedToday,
        byDataSource
      }
    } catch (error) {
      console.error('Error getting import stats:', error)
      return {
        totalContacts: 0,
        importedToday: 0,
        byDataSource: {}
      }
    }
  }
}