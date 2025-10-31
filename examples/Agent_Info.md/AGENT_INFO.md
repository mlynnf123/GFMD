Quick Start (Both Services)

  # Terminal 1 - Backend API
  cd /Users/merandafreiner/gfmd_swarm_agent && python3 dashboard_api.py

  # Terminal 2 - Frontend Dashboard
  cd /Users/merandafreiner/gfmd_swarm_agent/dashboard && npm run dev

  Then visit http://localhos
  t:3000 to access your dashboard!




Agent Workflow Process:

  1. 🏥 Hospital Prospecting Agent
    - Analyzes hospital data (bed count, lab types, equipment age)
    - Calculates qualification score (0-10 scale)
    - Recommends specific products (MACH, ELITE, STEALTH series)
    - Determines priority level (High/Medium/Low)
  2. 📧 Multi-Channel Outreach Agent
    - Creates personalized email sequences
    - Generates LinkedIn messages
    - Plans phone call schedules
    - Executes 8+ touchpoints over time
  3. 🎯 Vector-Enhanced Agents (Your new addition)
    - Research Agent: Finds relevant company info for prospects
    - Email Agent: Uses your knowledge base for personalization
    - LinkedIn Agent: References your success stories
    - Proposal Agent: Creates comprehensive proposals

  Manual vs Automated Triggering:

  Manual (What you'll test):
  result = await orchestrator.process_new_prospect(prospect_data)

  Automated Options:
  - Batch Processing: Process CSV files of leads
  - Real-time Monitoring: Auto-process new CRM entries
  - API Integration: Webhook triggers from your systems
  - Scheduled Jobs: Daily/weekly prospect processing

 🔧 Quick Commands:

  # Check status anytime
  python3 monitor_daily_runs.py

  # Run manually for testing  
  python3 daily_scheduler.py --run-now

  # View live logs
  tail -f logs/daily_scheduler_$(date +%Y%m%d).log


  How to Use:

  # Set your Groq key (already have it)
  export GROQ_API_KEY="your_groq_api_key_here"

  # Test with 10 prospects (dry run - doesn't actually send)
  python3 run_campaign.py 10

  # ACTUALLY SEND 50 emails
  python3 run_campaign.py 50 send