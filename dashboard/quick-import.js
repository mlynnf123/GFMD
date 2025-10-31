const fs = require('fs')

// Quick sample data creator for testing
const sampleContacts = [
  {
    executive_name: "Dr. Sarah Johnson",
    title: "Laboratory Director", 
    business_email: "sjohnson@houstonmethodist.org",
    hospital_name: "Houston Methodist Hospital",
    city: "Houston",
    state: "TX",
    qualification_score: 8
  },
  {
    executive_name: "Michael Chen",
    title: "Director of Laboratory Services",
    business_email: "michael.chen@bswhealth.com", 
    hospital_name: "Baylor Scott & White Medical Center",
    city: "Temple",
    state: "TX", 
    qualification_score: 7
  },
  {
    executive_name: "Dr. Patricia Williams",
    title: "Clinical Lab Director",
    business_email: "pwilliams@memorialhermann.org",
    hospital_name: "Memorial Hermann Texas Medical Center", 
    city: "Houston",
    state: "TX",
    qualification_score: 9
  },
  {
    executive_name: "Robert Garcia",
    title: "Chief Laboratory Officer", 
    business_email: "robert.garcia@utsouthwestern.edu",
    hospital_name: "UT Southwestern Medical Center",
    city: "Dallas", 
    state: "TX",
    qualification_score: 10
  },
  {
    executive_name: "Jennifer Martinez",
    title: "Laboratory Manager",
    business_email: "jmartinez@texaschildrens.org", 
    hospital_name: "Texas Children's Hospital",
    city: "Houston",
    state: "TX",
    qualification_score: 6
  }
]

console.log('🚀 Quick sample data created for testing')
console.log('📊 Sample contains 5 qualified healthcare contacts')
console.log('✅ All have valid emails and qualification scores')
console.log('\nTo populate database:')
console.log('1. Navigate to http://localhost:3001/settings') 
console.log('2. Use the import section with actual CSV files')
console.log('3. Or use the dashboard import interface')

// Save as JSON for reference
fs.writeFileSync('sample-contacts.json', JSON.stringify(sampleContacts, null, 2))
console.log('📁 Sample data saved as sample-contacts.json')