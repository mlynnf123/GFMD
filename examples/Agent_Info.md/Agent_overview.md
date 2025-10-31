 🤖 AGENT TYPES OVERVIEW

  Core Agent Architecture

  - BaseAIAgent - Foundation class with Vertex AI integration, memory, and async handling
  - CoordinatorAgent - Master orchestrator managing workflow stages
  - ResearchAgent - Deep web research and intelligence gathering
  - QualificationAgent - Lead scoring with ICP matching
  - EmailComposerAgent - Natural email generation following strict style rules

  Production Systems

  - ProductionVertexAIOnly - Gemini 2.5 Pro with real web search
  - ProductionAIResearchSystem - Research + email generation pipeline
  - AutomatedDailySystem - Daily processing of 50 contacts

  🔄 HOW AGENTS WORK TOGETHER

  Data Sources → Research Agent → Qualification Agent → Email Agent → Delivery
       ↓              ↓                ↓                  ↓           ↓
  Google Sheets   Web Search      ICP Scoring      Natural Email   Gmail API
  Definitive      Vertex AI       Lead Priority    Generation      Tracking
  Healthcare      Analysis        Ranking          (T=0.9)         Limits

  Coordination Flow:
  1. Coordinator assigns tasks to specialized agents
  2. Research Agent conducts 3-4 web searches per prospect + Vertex AI analysis
  3. Qualification Agent scores leads based on ICP fit
  4. Email Agent writes natural emails using research insights
  5. Integration agents handle Gmail sending and Sheets logging

  ⚙️ CURRENT AUTOMATIONS

  Daily Automation

  - Target: 50 real contacts daily from Definitive Healthcare
  - Schedule: 9:00 AM CST (scheduled but not currently running)
  - Process: Research → Qualify → Email → Log
  - Status: Last run 9/10, processed row 106