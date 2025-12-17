# Dashboard Design for GFMD AI Swarm

## Recommended Tech Stack

**Simple, Modern, Fast:**
- **Backend**: Flask API (Python) - serves data from CSV/JSON
- **Frontend**: React/Next.js with Tailwind CSS
- **Charts**: Recharts or Chart.js
- **Real-time**: WebSocket for live logs

---

## Pages & Features

### 1. **OVERVIEW / DASHBOARD** (Main Page)

**Purpose**: At-a-glance view of system health and performance

**Key Metrics Cards:**

```
┌────────────────────┬────────────────────┬────────────────────┐
│  EMAILS SENT       │  SUCCESS RATE      │  HIGH PRIORITY     │
│  Today: 47         │  94.2%             │  35 leads          │
│  This Week: 312    │  ▲ 2.1% vs avg     │  ▲ 12 vs yesterday │
└────────────────────┴────────────────────┴────────────────────┘

┌────────────────────┬────────────────────┬────────────────────┐
│  AVG QUAL SCORE    │  AI COST TODAY     │  CONTACTS READY    │
│  78.5/100          │  $0.08             │  9,847             │
│  ▲ 3.2 vs avg      │  (~$0.0017/email)  │  (95.8%)           │
└────────────────────┴────────────────────┴────────────────────┘
```

**Charts:**
- **Line chart**: Emails sent over time (last 30 days)
- **Bar chart**: Priority distribution (HIGH/MEDIUM/LOW) by week
- **Donut chart**: Success/Fail/Pending email status
- **Map (optional)**: Contacts by state (heatmap)

**Recent Activity Feed:**
```
📧 Email sent to Dr. Lauren Anthony (Abbott Northwestern) - Score: 90
🎯 High priority lead found: Abrazo Health - Score: 85
✅ Campaign completed: 50 emails sent, 47 successful
❌ Email failed: invalid@example.com - Bounced
```

**Quick Actions:**
- "Run New Campaign" button (prominent)
- "View Latest Logs" link
- "Download Campaign Report" link

---

### 2. **CAMPAIGNS** Page

**Purpose**: Create, run, and review campaigns

**Campaign Builder:**
```
┌─────────────────────────────────────────────┐
│  CREATE NEW CAMPAIGN                        │
├─────────────────────────────────────────────┤
│  Number of prospects: [___50___] ↕         │
│                                             │
│  Min qualification score: [___50___] ↕      │
│  (Only send to prospects scoring above)     │
│                                             │
│  Mode: ◉ Dry Run  ○ Send Emails           │
│                                             │
│  [   START CAMPAIGN   ]                    │
└─────────────────────────────────────────────┘
```

**Campaign History Table:**
```
┌──────────────┬─────────┬──────────┬─────────┬────────┬─────────┐
│ Campaign ID  │ Date    │ Sent     │ Success │ Failed │ Actions │
├──────────────┼─────────┼──────────┼─────────┼────────┼─────────┤
│ campaign_... │ 10/31   │ 50       │ 47      │ 3      │ [View]  │
│ campaign_... │ 10/30   │ 50       │ 49      │ 1      │ [View]  │
│ campaign_... │ 10/29   │ 50       │ 48      │ 2      │ [View]  │
└──────────────┴─────────┴──────────┴─────────┴────────┴─────────┘
```

**Campaign Detail View (when clicked):**
- Campaign metadata (date, duration, tokens used)
- List of all prospects processed
- For each prospect:
  - Name, company, email
  - Qualification score
  - Email preview (with expand/collapse)
  - Status (sent/failed/skipped)
  - Reason for skip (if applicable)

---

### 3. **CONTACTS** Page

**Purpose**: Browse and search the 10,283 healthcare contacts

**Filter Bar:**
```
Search: [_________________] 🔍
State: [All States ▾]  Facility Type: [All Types ▾]
Status: ◉ All  ○ Never Contacted  ○ Ready  ○ In Cooldown
```

**Contact Table:**
```
┌──────────────────┬─────────────────────────┬───────────┬──────────┬────────────┬──────────┐
│ Name             │ Company                 │ Title     │ Location │ Status     │ Last     │
│                  │                         │           │          │            │ Contact  │
├──────────────────┼─────────────────────────┼───────────┼──────────┼────────────┼──────────┤
│ Dr. Lauren       │ Abbott Northwestern     │ Lab Dir   │ MN       │ Contacted  │ 10/31    │
│ Anthony          │ Hospital                │           │          │            │          │
├──────────────────┼─────────────────────────┼───────────┼──────────┼────────────┼──────────┤
│ Elizabeth Boone  │ Abbeville Area Medical  │ Lab Dir   │ SC       │ Ready      │ Never    │
├──────────────────┼─────────────────────────┼───────────┼──────────┼────────────┼──────────┤
│ Julie Koller     │ Abrazo Arrowhead        │ Lab Dir   │ AZ       │ Cooldown   │ 10/15    │
└──────────────────┴─────────────────────────┴───────────┴──────────┴────────────┴──────────┘

Showing 1-25 of 10,283  [< Prev] [Next >]
```

**Contact Detail Modal (click a row):**
```
┌─────────────────────────────────────────────┐
│  Dr. Lauren Anthony                         │
│  Abbott Northwestern Hospital               │
├─────────────────────────────────────────────┤
│  📧 lauren.anthony@allina.com              │
│  📞 (612) 863-0409                         │
│  📍 Minneapolis, MN                        │
│  🏥 Short Term Acute Care Hospital         │
│                                             │
│  Status: Contacted                          │
│  Last Contact: October 31, 2025            │
│  Email Count: 1                             │
│  Best Score: 90/100 (HIGH)                 │
│                                             │
│  Email History:                             │
│  • Oct 31: "Quieter Centrifuges..." ✅     │
│                                             │
│  [View Full History] [Mark as Do Not Contact]│
└─────────────────────────────────────────────┘
```

**Summary Stats at Top:**
```
Total: 10,283  |  Never Contacted: 9,847  |  Ready: 9,847  |  In Cooldown: 436
```

---

### 4. **ANALYTICS** Page

**Purpose**: Deeper insights and trends

**Time Range Selector:**
```
View: ○ Last 7 Days  ◉ Last 30 Days  ○ Last 90 Days  ○ All Time
```

**Charts Section:**

1. **Email Performance Over Time** (Line chart)
   - X-axis: Date
   - Y-axis: Number of emails
   - Lines: Sent (green), Failed (red), High Priority (blue)

2. **Qualification Score Distribution** (Histogram)
   - X-axis: Score ranges (0-20, 21-40, 41-60, 61-80, 81-100)
   - Y-axis: Count of prospects
   - Color code: RED (<50), YELLOW (50-69), GREEN (70+)

3. **Success Rate by State** (Bar chart)
   - X-axis: States (top 10 by volume)
   - Y-axis: Success rate %
   - Sorted by volume

4. **Facility Type Breakdown** (Donut chart)
   - Short Term Acute Care: 65%
   - Critical Access: 20%
   - Health Systems: 10%
   - Other: 5%

5. **AI Cost Trends** (Line chart)
   - X-axis: Date
   - Y-axis: Cost ($)
   - Show: Daily cost, Cumulative cost

6. **Response Time Distribution** (Box plot or histogram)
   - How long AI takes to process each prospect
   - Shows: Min, Avg, Max, P95, P99

**Key Insights Cards:**
```
┌────────────────────────────────────────────┐
│  BEST PERFORMING STATES                    │
│  1. Texas - 87% success rate               │
│  2. California - 85% success rate          │
│  3. Florida - 83% success rate             │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  TOP FACILITY TYPES                        │
│  1. Short Term Acute Care - 78.5 avg score │
│  2. Health Systems - 76.2 avg score        │
│  3. Critical Access - 72.1 avg score       │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  COST EFFICIENCY                           │
│  Avg cost per email: $0.0016               │
│  Avg cost per HIGH lead: $0.0018           │
│  Total spent (all time): $16.45            │
└────────────────────────────────────────────┘
```

---

### 5. **LOGS** Page

**Purpose**: Real-time system monitoring

**Live Log Stream:**
```
┌──────────────────────────────────────────────────────────────┐
│  🔴 LIVE    Clear Logs    Download    Pause                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [11:02:18] INFO: Campaign started: campaign_20251031_110218│
│  [11:02:18] INFO: Loaded 50 contacts from CSV              │
│  [11:02:19] INFO: [1/50] Processing: Abbott Northwestern...│
│  [11:02:19] INFO:   → Research stage...                    │
│  [11:02:20] INFO:   → Qualification stage...               │
│  [11:02:21] INFO:   → Score: 90/100 (HIGH)                 │
│  [11:02:21] INFO:   → Email composition stage...           │
│  [11:02:22] INFO:   ✓ Email composed successfully         │
│  [11:02:22] INFO:   ✓ Email sent to lauren.anthony@...    │
│  [11:02:22] INFO: [2/50] Processing: Abrazo Health...     │
│  [11:02:23] ERROR:  ✗ Gmail send failed: Rate limit       │
│  [11:02:23] INFO: Waiting 5 seconds before retry...       │
│                                                              │
│  Auto-scroll: ☑  Level: ◉ All  ○ Info  ○ Warnings  ○ Errors│
└──────────────────────────────────────────────────────────────┘
```

**Filter Options:**
- Log level: All / Info / Warning / Error
- Search logs: [____________] 🔍
- Time range: Last 1 hour / 24 hours / 7 days

**Log Statistics:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  INFO       │  WARNING    │  ERROR      │  TOTAL      │
│  1,247      │  23         │  5          │  1,275      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Recent Errors (if any):**
```
⚠️ 5 errors in the last 24 hours:
  • 10/31 11:02 - Gmail send failed: Rate limit exceeded
  • 10/31 10:45 - Invalid email format: badformat@
  • 10/31 09:12 - Groq API timeout after 30s
```

---

### 6. **SETTINGS** Page

**Purpose**: Configure system behavior

**Email Settings:**
```
┌─────────────────────────────────────────────┐
│  EMAIL CONFIGURATION                        │
├─────────────────────────────────────────────┤
│  Daily email limit:    [___100___]         │
│  Re-contact interval:  [____30___] days    │
│  Sender name:          [Mark Thompson____] │
│  Sender email:         [mark@gfmdmedical] │
│                                             │
│  [Save Changes]                            │
└─────────────────────────────────────────────┘
```

**AI Configuration:**
```
┌─────────────────────────────────────────────┐
│  AI AGENT SETTINGS                          │
├─────────────────────────────────────────────┤
│  Groq API Key: [gsk_WYKA...fkyL___] [Test]│
│                                             │
│  Model: [llama-3.3-70b-versatile ▾]       │
│                                             │
│  Temperature:                               │
│    Research Agent:       [0.3_____]        │
│    Qualification Agent:  [0.2_____]        │
│    Email Composer:       [0.7_____]        │
│                                             │
│  [Save Changes]  [Reset to Defaults]      │
└─────────────────────────────────────────────┘
```

**Qualification Thresholds:**
```
┌─────────────────────────────────────────────┐
│  LEAD SCORING                               │
├─────────────────────────────────────────────┤
│  Minimum score to send email: [__50__]/100 │
│                                             │
│  Priority Levels:                           │
│    HIGH:   [_70_] - 100                    │
│    MEDIUM: [_50_] - 69                     │
│    LOW:    0 - 49                          │
│                                             │
│  [Save Changes]                            │
└─────────────────────────────────────────────┘
```

**System Information:**
```
┌─────────────────────────────────────────────┐
│  SYSTEM STATUS                              │
├─────────────────────────────────────────────┤
│  Gmail API:    ✅ Connected                │
│  Groq API:     ✅ Connected                │
│  Storage:      ✅ campaign_tracking.json   │
│  Contacts CSV: ✅ 10,283 contacts loaded   │
│                                             │
│  Version: 2.0.0-groq                       │
│  Last Updated: October 31, 2025            │
└─────────────────────────────────────────────┘
```

**Danger Zone:**
```
┌─────────────────────────────────────────────┐
│  ⚠️ DANGER ZONE                            │
├─────────────────────────────────────────────┤
│  [Clear All Campaign History]              │
│  [Reset All Contact Tracking]              │
│  [Export Data & Backup]                    │
└─────────────────────────────────────────────┘
```

---

## Essential KPIs Summary

### Primary Metrics (Show Everywhere):
1. **Emails Sent** (today/week/month/all-time)
2. **Success Rate** (sent / attempted)
3. **Average Qualification Score** (0-100)
4. **High Priority Leads** (count)
5. **AI Cost** (dollars per day/week/campaign)

### Secondary Metrics:
6. **Contacts Ready for Outreach** (off cooldown)
7. **Processing Speed** (prospects/minute)
8. **Token Usage** (cost tracking)
9. **Email Failure Rate** (%)
10. **Geographic Distribution** (top states/regions)

### Operational Metrics:
11. **System Uptime** (if running as service)
12. **API Response Time** (Groq + Gmail)
13. **Error Rate** (errors per 100 operations)
14. **Campaign Completion Time** (minutes)
15. **Storage Used** (MB for tracking.json)

---

## Mobile Considerations

**Mobile-Friendly Views:**
- Dashboard: Stack cards vertically
- Campaigns: Simplified table (hide less critical columns)
- Contacts: Card view instead of table
- Logs: Condensed view with expand
- Analytics: One chart per screen, swipeable

---

## Implementation Priority

### Phase 1 (MVP):
1. ✅ Overview/Dashboard - Main KPIs
2. ✅ Campaigns - Create and run
3. ✅ Logs - Real-time viewing

### Phase 2:
4. ✅ Contacts - Browse database
5. ✅ Settings - Basic configuration

### Phase 3:
6. ✅ Analytics - Charts and trends
7. ✅ Email previews
8. ✅ Export/reporting

### Phase 4 (Nice to Have):
9. ⬜ Real-time WebSocket updates
10. ⬜ Email open/click tracking
11. ⬜ A/B testing different email templates
12. ⬜ Scheduled campaigns (cron GUI)
13. ⬜ Multi-user access/permissions

---

## Tech Notes

**Backend API Endpoints Needed:**
```
GET  /api/metrics           - Dashboard KPIs
GET  /api/campaigns         - List campaigns
POST /api/campaigns/run     - Start new campaign
GET  /api/campaigns/:id     - Campaign details
GET  /api/contacts          - List contacts (paginated)
GET  /api/contacts/:email   - Contact details
GET  /api/analytics         - Analytics data
GET  /api/logs              - Recent logs
WS   /api/logs/stream       - Live log stream
GET  /api/settings          - Get settings
POST /api/settings          - Update settings
GET  /api/stats             - System stats
```

**Data Sources:**
- `campaign_tracking.json` - All campaign data
- `definitive_healthcare_data.csv` - Contact database
- Groq agent metrics (in-memory during run)
- Log files in `logs/` directory

---

## UI Framework Recommendation

**Best Options:**

1. **Next.js + Tailwind + shadcn/ui** ⭐ Recommended
   - Modern, fast, great DX
   - Components pre-built
   - Easy deployment

2. **React + Vite + Tailwind + Recharts**
   - Faster dev server
   - Simpler than Next.js
   - Good for SPA

3. **Streamlit** (Python-native)
   - Fastest to build
   - All Python, no JS
   - Limited customization

**Recommendation**: Go with Next.js + Tailwind. It's what you already started, modern, and perfect for this use case.

