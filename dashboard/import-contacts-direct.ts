import * as fs from 'fs'
import { ContactImportService } from './lib/contact-import-service'

async function importContacts() {
  console.log('🚀 Starting direct contact import...')
  
  const importService = new ContactImportService()
  
  try {
    // Import the definitive healthcare data first
    console.log('📋 Importing Definitive Healthcare data...')
    const definitiveCSV = fs.readFileSync('/Users/merandafreiner/gfmd_swarm_agent/definitive_healthcare_data.csv', 'utf8')
    
    const definitiveResult = await importService.importContactsFromCSV(definitiveCSV)
    console.log('✅ Definitive Healthcare import completed:', definitiveResult)
    
    // Import the verified contacts
    console.log('\n📋 Importing verified contacts...')
    const verifiedCSV = fs.readFileSync('/Users/merandafreiner/gfmd_swarm_agent/verified_contacts_template.csv', 'utf8')
    
    const verifiedResult = await importService.importContactsFromCSV(verifiedCSV)
    console.log('✅ Verified contacts import completed:', verifiedResult)
    
    // Get final stats
    const stats = await importService.getImportStats()
    console.log('\n📊 Final Database Statistics:')
    console.log(`   • Total contacts: ${stats.totalContacts.toLocaleString()}`)
    console.log(`   • Imported today: ${stats.importedToday}`)
    console.log('   • By source:')
    Object.entries(stats.byDataSource).forEach(([source, count]) => {
      console.log(`     - ${source}: ${count}`)
    })
    
    console.log('\n🎉 Import completed successfully!')
    
  } catch (error) {
    console.error('❌ Import failed:', error)
  }
}

importContacts()