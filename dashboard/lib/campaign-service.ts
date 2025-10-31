// Campaign service to interact with your GFMD system
export class CampaignService {
  // Direct API to your dashboard server
  private readonly API_BASE = 'http://localhost:8080'

  async runEmailCampaign(emailCount: number = 50): Promise<{ success: boolean; message: string; data?: any }> {
    try {
      console.log(`Attempting to run ${emailCount} emails via API...`)
      
      // Use the quick-run endpoint for immediate execution
      const response = await fetch(`${this.API_BASE}/api/v1/automation/quick-run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          num_emails: emailCount
        }),
        // Add timeout and error handling
        signal: AbortSignal.timeout(30000) // 30 second timeout
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown API error' }))
        throw new Error(errorData.message || `API returned ${response.status}`)
      }

      const data = await response.json()
      console.log('API Response:', data)
      
      return {
        success: data.success,
        message: data.message || `Successfully sent ${data.emails_sent} emails`,
        data
      }
    } catch (error) {
      console.error('Campaign API error:', error)
      
      // Check if it's a connection error (API not running)
      if (error instanceof TypeError || (error as any).name === 'TypeError') {
        console.log('API connection failed, API server may not be running')
        return {
          success: false,
          message: `❌ Dashboard API Server Not Running\n\nThe email campaign API at ${this.API_BASE} is not responding.\n\nPlease ensure the API server is running:\n\n1. Open terminal\n2. cd /Users/merandafreiner/gfmd_swarm_agent  \n3. python3 dashboard_api.py\n\nThen try the campaign again.`
        }
      }
      
      return {
        success: false,
        message: `API Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`
      }
    }
  }

  async runLocalCampaign(emailCount: number = 50): Promise<{ success: boolean; message: string; data?: any }> {
    try {
      // Execute the actual production system command
      const command = `cd /Users/merandafreiner/gfmd_swarm_agent && python3 -c "
import asyncio
from production_system import FirestoreProductionSystem

async def run():
    system = FirestoreProductionSystem()
    result = await system.run_daily_automation(num_prospects=${emailCount})
    return result

asyncio.run(run())
"`
      
      // For now, since we can't directly execute Python from browser, 
      // we'll need to call your API endpoint
      return {
        success: false,
        message: `To run ${emailCount} real emails, execute this command:\n\ncd /Users/merandafreiner/gfmd_swarm_agent\npython3 -c "import asyncio; from production_system import FirestoreProductionSystem; asyncio.run(FirestoreProductionSystem().run_daily_automation(${emailCount}))"`
      }
    } catch (error) {
      return {
        success: false,
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      }
    }
  }

  async checkSystemStatus(): Promise<{ 
    gmail: boolean; 
    firestore: boolean; 
    vertexai: boolean; 
    emailsToday: number 
  }> {
    try {
      const response = await fetch(`${this.API_BASE}/v1/system/status`)
      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      console.error('Status check failed:', error)
    }

    // Default status
    return {
      gmail: true,
      firestore: true,
      vertexai: false, // Based on previous Vertex AI issues
      emailsToday: 0
    }
  }
}