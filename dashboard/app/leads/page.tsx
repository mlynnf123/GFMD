"use client"

import { useState, useEffect, Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { MetricCard } from "@/components/metric-card"
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from "recharts"
import { FirestoreService, Contact } from "@/lib/firestore-service"
import { collection, query, limit, getDocs, where, orderBy } from "firebase/firestore"
import { db } from "@/lib/firebase"

function ContactsPageContent() {
  const searchParams = useSearchParams()
  const [searchTerm, setSearchTerm] = useState(searchParams.get('search') || "")
  const [selectedFilter, setSelectedFilter] = useState("all")
  const [contactsData, setContactsData] = useState<Contact[]>([])
  const [facilityTypeData, setFacilityTypeData] = useState<any[]>([])
  const [stateData, setStateData] = useState<any[]>([])
  const [stats, setStats] = useState({
    total: 0,
    qualified: 0,
    neverContacted: 0,
    avgQualificationScore: 0
  })
  const [loading, setLoading] = useState(true)
  const firestoreService = new FirestoreService()

  const getQualificationColor = (score: number) => {
    if (score >= 8) return "sentiment-positive"
    if (score >= 6) return "sentiment-neutral" 
    return "sentiment-negative"
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "qualified": return "status-interested"
      case "contacted": return "status-cold"
      default: return "sentiment-neutral"
    }
  }

  useEffect(() => {
    loadContactsData()
  }, [])

  const loadContactsData = async () => {
    try {
      setLoading(true)
      
      // Get contact stats
      const contactStats = await firestoreService.getContactStats()
      setStats(contactStats)
      
      // Get recent contacts
      const contactsRef = collection(db, 'healthcare_contacts')
      const contactsQuery = query(
        contactsRef,
        orderBy('qualification_score', 'desc'),
        limit(50)
      )
      const contactsSnapshot = await getDocs(contactsQuery)
      const contacts: Contact[] = []
      
      contactsSnapshot.forEach((doc) => {
        contacts.push({
          id: doc.id,
          ...doc.data()
        } as Contact)
      })
      setContactsData(contacts)
      
      // Calculate facility type distribution
      const facilityTypes: { [key: string]: number } = {}
      const states: { [key: string]: number } = {}
      
      contacts.forEach((contact) => {
        // Facility types
        const facility = contact.facility_type || 'Unknown'
        facilityTypes[facility] = (facilityTypes[facility] || 0) + 1
        
        // States
        const state = contact.state || 'Unknown'
        states[state] = (states[state] || 0) + 1
      })
      
      // Convert to chart data
      const colors = ['#70a9ff', '#9370db', '#ff70a3', '#70ffb9', '#ffd670']
      const facilityData = Object.entries(facilityTypes)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([ name, value], index) => ({
          name,
          value,
          color: colors[index % colors.length]
        }))
      setFacilityTypeData(facilityData)
      
      const stateChartData = Object.entries(states)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([state, contacts]) => ({
          state,
          contacts
        }))
      setStateData(stateChartData)
      
    } catch (error) {
      console.error('Error loading contacts:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredContacts = contactsData.filter(contact => {
    const matchesSearch = searchTerm === '' || 
      contact.contact_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.email?.toLowerCase().includes(searchTerm.toLowerCase())
    
    return matchesSearch
  })

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight gradient-text">Contacts</h1>
          <p className="text-muted-foreground mt-1">
            Healthcare contact database with 10,000+ verified professionals
          </p>
        </div>
        <Button 
          className="glossy-button"
          onClick={() => {
            alert('Import Contacts feature coming soon!\n\nTo add contacts:\n1. Update definitive_healthcare_data.csv\n2. Run: python simple_migrate.py\n3. Deploy the updated system')
          }}
        >
          Import Contacts
        </Button>
      </div>

      {/* Contact Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Contacts"
          value={stats.total.toLocaleString()}
          description="Verified healthcare professionals"
        />
        
        <MetricCard
          title="Qualified Contacts"
          value={stats.qualified.toLocaleString()}
          description="Score 7+ ready for outreach"
        />
        
        <MetricCard
          title="Never Contacted"
          value={stats.neverContacted.toLocaleString()}
          description="Fresh prospects available"
        />
        
        <MetricCard
          title="Avg Qualification Score"
          value={stats.avgQualificationScore.toFixed(1)}
          description="Across all contacts"
        />
      </div>

      {/* Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Facility Types */}
        <div className="metric-card">
          <h3 className="text-lg font-semibold mb-4">Contacts by Facility Type</h3>
          <div className="flex items-center justify-between">
            <ResponsiveContainer width="60%" height={200}>
              <PieChart>
                <Pie
                  data={facilityTypeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  dataKey="value"
                >
                  {facilityTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {facilityTypeData.map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div 
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <div className="text-sm">
                    <span className="font-medium">{item.name}</span>
                    <div className="text-muted-foreground">{item.value.toLocaleString()}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Geographic Distribution */}
        <div className="metric-card">
          <h3 className="text-lg font-semibold mb-4">Top States by Contact Count</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={stateData} layout="horizontal">
              <XAxis type="number" stroke="#9CA3AF" />
              <YAxis dataKey="state" type="category" stroke="#9CA3AF" />
              <Bar dataKey="contacts" fill="#70a9ff" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="metric-card">
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search contacts by name, organization, or title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-3 pr-3 py-2 bg-secondary border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <Button 
            variant="ghost"
            onClick={() => alert('Filter options coming soon! You can currently use the search bar to filter contacts by name, organization, title, or email.')}
          >
            Filters
          </Button>
        </div>

        {/* Contact List */}
        <div className="space-y-3">
          {loading ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Loading contacts...</p>
            </div>
          ) : filteredContacts.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No contacts found</p>
            </div>
          ) : (
            filteredContacts.map((contact) => (
            <div key={contact.id} className="p-4 rounded-lg bg-secondary/30 border border-border/50 hover:bg-secondary/50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center">
                      <span className="font-medium text-sm">
                        {contact.contact_name?.split(' ').map(n => n[0]).join('') || 'NA'}
                      </span>
                    </div>
                    <div>
                      <h4 className="font-semibold">{contact.contact_name || 'Unknown'}</h4>
                      <p className="text-sm text-muted-foreground">{contact.title || 'No title'}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                    <div>
                      <p className="text-xs text-muted-foreground">Organization</p>
                      <p className="text-sm font-medium">{contact.company_name || 'Unknown'}</p>
                      <p className="text-xs text-muted-foreground">{contact.facility_type || 'Healthcare'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Location</p>
                      <p className="text-sm">{contact.city && contact.state ? `${contact.city}, ${contact.state}` : 'Unknown'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Score</p>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getQualificationColor(contact.qualification_score || 0)}`}>
                        {contact.qualification_score || 0}/10
                      </span>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Status</p>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(contact.last_contacted ? 'contacted' : 'qualified')}`}>
                        {contact.last_contacted ? 'Contacted' : 'Not Contacted'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>{contact.email || 'No email'}</span>
                    <span>{contact.phone || 'No phone'}</span>
                    <span>Last contact: {contact.last_contacted ? new Date(contact.last_contacted.toDate()).toLocaleDateString() : 'Never'}</span>
                  </div>
                </div>
                
                <div className="flex gap-2 ml-4">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => {
                      alert(`Contact Details:\n\nName: ${contact.contact_name || 'Unknown'}\nTitle: ${contact.title || 'N/A'}\nOrganization: ${contact.company_name || 'Unknown'}\nEmail: ${contact.email || 'No email'}\nPhone: ${contact.phone || 'No phone'}\nScore: ${contact.qualification_score || 0}/10\n\nFull profile view coming soon!`)
                    }}
                  >
                    View Profile
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => {
                      if (!contact.email) {
                        alert('No email address available for this contact')
                        return
                      }
                      const subject = encodeURIComponent('GFMD Medical Device Solutions')
                      const body = encodeURIComponent(`Dear ${contact.contact_name || 'Healthcare Professional'},\n\nI hope this message finds you well...`)
                      window.open(`mailto:${contact.email}?subject=${subject}&body=${body}`)
                    }}
                  >
                    Send Email
                  </Button>
                </div>
              </div>
            </div>
          ))
          )}
        </div>
      </div>
    </div>
  )
}

export default function ContactsPage() {
  return (
    <Suspense fallback={<div className="p-6"><p>Loading...</p></div>}>
      <ContactsPageContent />
    </Suspense>
  )
}