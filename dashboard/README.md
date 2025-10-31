# GFMD AI Swarm Agent Dashboard

A modern, dark-themed dashboard for monitoring and managing the GFMD AI Swarm Agent system built with Next.js, Tailwind CSS, and Shadcn UI.

## Features

🎯 **Operational Command Center**
- Real-time email campaign status and progress
- System health indicators for all components
- Manual campaign launch controls
- Live success rate monitoring

📈 **Business Intelligence**
- Healthcare contact database overview (10,000+ contacts)
- Geographic distribution and facility type analytics
- Campaign performance trends and metrics
- AI agent performance monitoring

📧 **Email Campaign Management**
- Daily email progress tracking (target: 50/day)
- Success/failure breakdown with detailed reasons
- Email verification and formatting compliance
- Recent activity monitoring

🤖 **AI Agent Performance**
- Real-time monitoring of all 4 agents (Coordinator, Research, Qualification, Email Composer)
- Token usage and cost tracking
- Performance metrics and bottleneck identification
- A2A communication flow analysis

## Quick Start

1. **Install Dependencies**
   ```bash
   cd dashboard
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your Firebase configuration
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Build for Production**
   ```bash
   npm run build
   npm start
   ```

## Environment Variables

Configure these in your `.env.local` file:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=windy-tiger-471523-m5
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom dark theme
- **UI Components**: Shadcn UI with glassmorphism effects
- **Charts**: Recharts for data visualization
- **Database**: Firestore for real-time data
- **TypeScript**: Full type safety

## Dashboard Tabs

### 📊 Dashboard (Main)
- Daily email progress (56/100 sent today)
- Success rate trends and metrics
- AI agent activity monitoring
- Recent email activity feed

### 📧 Campaigns
- Active campaign management
- Email batch controls (5, 25, 50 emails)
- Campaign performance analytics
- Success rate monitoring

### 👥 Contacts
- Healthcare database with 10,247 contacts
- Qualification score filtering (7+ qualified)
- Geographic and facility type distribution
- Contact search and management

### 🤖 AI Agents
- Real-time agent performance monitoring
- Token usage and cost tracking
- System resource utilization
- Error logging and diagnostics

## Key Metrics

- **Daily Email Target**: 50 emails per day
- **Success Rate**: 94% average delivery
- **Contact Database**: 10,000+ verified healthcare professionals
- **Qualification Threshold**: Score 7+ for outreach
- **AI Agents**: 4 specialized agents in the pipeline

## API Integration

The dashboard connects to your existing GFMD system through:
- Firestore real-time database
- Cloud Run API endpoints
- Gmail API integration
- Vertex AI monitoring

## Deployment

Deploy to Vercel, Netlify, or any Node.js hosting provider:

```bash
npm run build
# Deploy the .next folder and package.json
```

## Support

For questions about the GFMD AI Swarm Agent system or dashboard configuration, refer to the main project documentation in the parent directory.