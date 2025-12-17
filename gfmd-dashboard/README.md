# GFMD Email Automation Dashboard

A real-time monitoring dashboard for the GFMD email automation system, displaying live data from your Railway deployment.

## Features

- **Real-time monitoring** of email sequences
- **Live connection** to Railway MongoDB database  
- **Email performance tracking** (sent, opens, replies)
- **Revenue visualization** with charts
- **Lead activity monitoring**
- **System status indicators**
- **Auto-refresh** every 30 seconds

## Technology Stack

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **MongoDB** connection to Railway database

## Design System

- **Colors**: White, black, grey, and light blue only
- **Typography**: Font weight 400 or less (400 for headings)
- **No emojis or icons**: Clean, minimal design
- **Responsive**: Works on desktop and mobile

## Local Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment variables**:
   Create `.env.local` with:
   ```env
   MONGODB_CONNECTION_STRING="your-mongodb-connection-string"
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Open dashboard**:
   Visit [http://localhost:3000](http://localhost:3000)

## Deployment to Vercel

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial GFMD dashboard"
   git remote add origin https://github.com/yourusername/gfmd-dashboard.git
   git push -u origin main
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Add environment variables:
     - `MONGODB_CONNECTION_STRING`: Your MongoDB connection string
   - Deploy

## Dashboard Sections

### System Status
- Real-time automation status
- Active/inactive indicators  
- Total sequence counts

### Hero Statistics
- Total Sales
- Active Sequences
- Reply Rate
- Open Rate

### Performance Charts
- **Email Performance**: 7-day trends
- **Revenue Growth**: Monthly progression

### Lead Activity
- Recent contact interactions
- Engagement status
- Response tracking

## Integration with Railway

This dashboard connects to the same MongoDB database as your Railway-deployed email automation system, providing real-time visibility into your GFMD automation performance.
