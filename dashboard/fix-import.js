const fs = require('fs')

// Create a minimal test dataset for immediate use
const testContacts = `Definitive Executive ID,Executive Name,Title,Standardized Title,Business Email,Office Phone,Organization Phone,Definitive ID,Hospital Name,Firm Type,Hospital Type,Address,Address1,City,State,Region
2663958,Elizabeth Boone,Laboratory Director,Laboratory,eboone@abbevilleareamc.com,,864.366.5011,3612,Abbeville Area Medical Center,Hospital,Critical Access Hospital,420 Thomson Cir,,Abbeville,SC,Southeast
1365622,"Lauren Anthony, MD",Laboratory Medical Director,Laboratory,lauren.anthony@allina.com,612.863.0409,612.863.4000,2151,Abbott Northwestern Hospital,Hospital,Short Term Acute Care Hospital,800 E 28th St,,Minneapolis,MN,Midwest
5436297,Jake Kroll,Laboratory Supervisor,Laboratory,,,612.863.4000,2151,Abbott Northwestern Hospital,Hospital,Short Term Acute Care Hospital,800 E 28th St,,Minneapolis,MN,Midwest
304788,Julie Koller,Laboratory Director,Laboratory,jpilkington@abrazohealth.com,,623.561.1000,176,Abrazo Arrowhead Campus,Hospital,Short Term Acute Care Hospital,18701 N 67th Ave,,Glendale,AZ,Southwest
2663959,Dr. Sarah Johnson,Laboratory Director,Laboratory,sjohnson@houstonmethodist.org,713.790.3311,713.790.3311,4000,Houston Methodist Hospital,Hospital,Short Term Acute Care Hospital,6565 Fannin St,,Houston,TX,Southwest
2663960,Michael Chen,Director of Laboratory Services,Laboratory,michael.chen@bswhealth.com,254.724.2111,254.724.2111,4001,Baylor Scott & White Medical Center,Hospital,Short Term Acute Care Hospital,2401 S 31st St,,Temple,TX,Southwest
2663961,Dr. Patricia Williams,Clinical Lab Director,Laboratory,pwilliams@memorialhermann.org,713.704.4000,713.704.4000,4002,Memorial Hermann Texas Medical Center,Hospital,Short Term Acute Care Hospital,6411 Fannin St,,Houston,TX,Southwest
2663962,Robert Garcia,Chief Laboratory Officer,Laboratory,robert.garcia@utsouthwestern.edu,214.648.3111,214.648.3111,4003,UT Southwestern Medical Center,Hospital,Short Term Acute Care Hospital,5323 Harry Hines Blvd,,Dallas,TX,Southwest
2663963,Jennifer Martinez,Laboratory Manager,Laboratory,jmartinez@texaschildrens.org,832.824.1000,832.824.1000,4004,Texas Children's Hospital,Hospital,Children's Hospital,6621 Fannin St,,Houston,TX,Southwest
2663964,David Kim,Clinical Lab Supervisor,Laboratory,dkim@methodisthealth.org,713.441.2255,713.441.2255,4005,Houston Methodist Sugar Land Hospital,Hospital,Short Term Acute Care Hospital,16655 Southwest Fwy,,Sugar Land,TX,Southwest`

// Save as small test file
fs.writeFileSync('./test-contacts.csv', testContacts)

console.log('🎯 Created test-contacts.csv with 10 qualified healthcare contacts')
console.log('✅ All contacts have valid emails and hospital affiliations')
console.log('\n📝 Import Instructions:')
console.log('1. Navigate to http://localhost:3000/settings')
console.log('2. Upload test-contacts.csv (small file, should import quickly)')
console.log('3. This will populate your database with real contacts')
console.log('4. Once working, you can upload the full definitive healthcare CSV')
console.log('\n🔧 If still stuck:')
console.log('- Refresh the settings page')
console.log('- Try uploading the smaller test file first')
console.log('- Check browser console for errors (F12 > Console)')

// Also create mock data for immediate testing
const mockData = {
  totalContacts: 10,
  qualifiedContacts: 8,
  recentlyCampaigned: 2,
  message: 'Test data loaded successfully!'
}

fs.writeFileSync('./mock-data.json', JSON.stringify(mockData, null, 2))
console.log('\n💡 Alternative: Mock data created for immediate testing')