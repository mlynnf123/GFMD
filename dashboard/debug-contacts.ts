import { collection, getDocs, addDoc, Timestamp } from 'firebase/firestore'
import { db } from './lib/firebase'

async function debugFirestoreContacts() {
  console.log('🔍 Debugging Firestore contacts...')
  
  try {
    // Check what collections exist
    const contactsRef = collection(db, 'healthcare_contacts')
    const snapshot = await getDocs(contactsRef)
    
    console.log(`📊 Total contacts in database: ${snapshot.size}`)
    
    if (snapshot.size === 0) {
      console.log('❌ No contacts found in healthcare_contacts collection!')
      console.log('🚀 Adding sample contacts for testing...')
      
      // Add some sample contacts directly to Firestore
      const sampleContacts = [
        {
          contact_name: "Dr. Sarah Johnson",
          email: "sjohnson@houstonmethodist.org",
          title: "Laboratory Director",
          company_name: "Houston Methodist Hospital",
          city: "Houston",
          state: "TX",
          qualification_score: 8,
          data_source: "manual_debug",
          imported_at: Timestamp.now(),
          email_sent_count: 0,
          last_contacted: null,
          research_status: "imported"
        },
        {
          contact_name: "Michael Chen",
          email: "michael.chen@bswhealth.com",
          title: "Director of Laboratory Services",
          company_name: "Baylor Scott & White Medical Center",
          city: "Temple",
          state: "TX",
          qualification_score: 7,
          data_source: "manual_debug",
          imported_at: Timestamp.now(),
          email_sent_count: 0,
          last_contacted: null,
          research_status: "imported"
        },
        {
          contact_name: "Dr. Patricia Williams",
          email: "pwilliams@memorialhermann.org",
          title: "Clinical Lab Director",
          company_name: "Memorial Hermann Texas Medical Center",
          city: "Houston",
          state: "TX",
          qualification_score: 9,
          data_source: "manual_debug",
          imported_at: Timestamp.now(),
          email_sent_count: 0,
          last_contacted: null,
          research_status: "imported"
        }
      ]
      
      for (const contact of sampleContacts) {
        await addDoc(contactsRef, contact)
        console.log(`✅ Added: ${contact.contact_name}`)
      }
      
      console.log(`🎉 Added ${sampleContacts.length} sample contacts to database`)
      
    } else {
      console.log('📋 Existing contacts found. Sample structures:')
      let count = 0
      snapshot.forEach((doc) => {
        if (count < 3) { // Show first 3 contacts
          console.log(`Contact ${count + 1}:`, {
            id: doc.id,
            data: doc.data()
          })
          count++
        }
      })
    }
    
  } catch (error) {
    console.error('❌ Error accessing Firestore:', error)
  }
}

debugFirestoreContacts()