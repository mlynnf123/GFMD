#!/usr/bin/env node

const fs = require('fs')
const path = require('path')

// Simple CSV import script to populate database
async function importCSVFiles() {
  console.log('🚀 Starting CSV import process...')
  
  try {
    // Read the definitive healthcare CSV
    const definitiveCSVPath = '/Users/merandafreiner/gfmd_swarm_agent/definitive_healthcare_data.csv'
    const verifiedCSVPath = '/Users/merandafreiner/gfmd_swarm_agent/verified_contacts_template.csv'
    
    console.log('📋 Reading CSV files...')
    
    if (fs.existsSync(definitiveCSVPath)) {
      const definitiveData = fs.readFileSync(definitiveCSVPath, 'utf8')
      console.log(`📊 Definitive Healthcare CSV: ${definitiveData.split('\n').length - 1} records`)
      
      // Save to a temporary file in dashboard for processing
      fs.writeFileSync('./temp_definitive.csv', definitiveData)
      console.log('✅ Saved definitive data to temp file')
    }
    
    if (fs.existsSync(verifiedCSVPath)) {
      const verifiedData = fs.readFileSync(verifiedCSVPath, 'utf8')
      console.log(`📊 Verified Contacts CSV: ${verifiedData.split('\n').length - 1} records`)
      
      // Save to a temporary file in dashboard for processing
      fs.writeFileSync('./temp_verified.csv', verifiedData)
      console.log('✅ Saved verified data to temp file')
    }
    
    console.log('\n🎯 Files are ready for import via the dashboard Settings page!')
    console.log('   1. Open http://localhost:3001/settings')
    console.log('   2. Use the CSV Import section')
    console.log('   3. Upload temp_definitive.csv first (10,000+ contacts)')
    console.log('   4. Then upload temp_verified.csv (verified contacts)')
    console.log('\n📝 The import service will automatically:')
    console.log('   • Check for duplicates based on email and ID')
    console.log('   • Add qualification scores based on titles')
    console.log('   • Skip contacts without emails')
    console.log('   • Handle both CSV formats automatically')
    
  } catch (error) {
    console.error('❌ Import preparation failed:', error)
  }
}

importCSVFiles()