# GFMD AI Swarm - Groq-Powered System

**Status**: ✅ FULLY WORKING

A blazing-fast, simple B2B email outreach system using Groq AI (no Google Cloud dependencies).

## What We Built

Completely refactored your system to remove all Google Cloud pain points:

### Old Stack (BROKEN):
- ❌ Vertex AI (permission errors)
- ❌ Firestore (permission errors)
- ❌ Google Sheets (unnecessary complexity)
- ❌ Cloud Run deployment issues
- ❌ Complex IAM permissions

### New Stack (WORKING):
- ✅ **Groq AI** - Blazing fast inference (500+ tokens/sec)
- ✅ **CSV/JSON** - Simple file-based storage
- ✅ **Gmail API** - Kept working integration
- ✅ **Manual execution** - Run campaigns when you want

## The System

### 3 AI Agents (All Groq-powered):

1. **Research Agent** (`groq_research_agent.py`)
   - Analyzes healthcare facilities
   - Identifies pain points
   - Assesses buying signals

2. **Qualification Agent** (`groq_qualification_agent.py`)
   - Scores leads 0-100
   - Classifies as HIGH/MEDIUM/LOW priority
   - Only sends emails to 50+ scores

3. **Email Composer Agent** (`groq_email_composer_agent.py`)
   - Writes human-sounding emails
   - Follows your styling rules (Hi [name], / Best,)
   - No AI buzzwords

### Data:
- 10,283 healthcare contacts from Definitive Healthcare CSV
- CSV/JSON tracking (no database needed)
- 30-day re-contact prevention

## How to Use

### Setup (One Time):

```bash
# 1. Set your Groq API key
export GROQ_API_KEY="your_groq_api_key_here"

# 2. Install Groq (already done)
pip install groq

# That's it! Gmail is already configured.
```

### Run Campaigns:

```bash
# Dry run - generate 5 emails but don't send
python3 run_campaign.py 5

# Dry run - generate 20 emails but don't send
python3 run_campaign.py 20

# ACTUALLY SEND 10 emails via Gmail
python3 run_campaign.py 10 send

# ACTUALLY SEND 50 emails via Gmail
python3 run_campaign.py 50 send
```

## What Happens When You Run:

1. ✅ Loads contacts from `definitive_healthcare_data.csv`
2. ✅ Skips anyone contacted in last 30 days
3. ✅ Research Agent analyzes each facility (Groq AI)
4. ✅ Qualification Agent scores 0-100 (Groq AI)
5. ✅ Email Composer writes personalized emails (Groq AI)
6. ✅ Only sends to prospects scoring 50+
7. ✅ Sends via Gmail API
8. ✅ Tracks in `campaign_tracking.json`

## Sample Results (From Real Test):

```
Processed: 3 prospects
Emails generated: 3
High priority leads: 3
Qualification scores: 85/100, 90/100, 90/100
AI tokens used: 8,404
Time: ~30 seconds

Sample Email:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
To: lauren.anthony@allina.com
Subject: Quieter Centrifuges for Abbott Northwestern Hospital

Hi Lauren,

I understand that noise from centrifuge equipment can be a challenge
at Abbott Northwestern Hospital, and that lab space is also at a
premium. Our centrifuges are designed to run quieter and take up
less space, which can help with OSHA compliance and staff satisfaction.

Might be worth a quick conversation to see if our equipment could help?

Best,
Mark Thompson
GFMD Medical Devices
mark@gfmdmedical.com
(555) 123-4567
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Cost Estimate:

**Groq Pricing** (as of 2025):
- Llama 3.3 70B: ~$0.59 per 1M tokens
- Average campaign: ~2,800 tokens per prospect
- **Cost per email: ~$0.0016** (0.16 cents!)
- **100 emails: ~$0.16**
- **1,000 emails: ~$1.60**

Compare to old Vertex AI: Unknown (permissions blocked)

## Files You Care About:

```
Core System:
├── run_campaign.py              ← Main script (run this!)
├── groq_coordinator.py          ← Orchestrates all agents
├── groq_research_agent.py       ← Research agent
├── groq_qualification_agent.py  ← Scoring agent
├── groq_email_composer_agent.py ← Email writer
├── groq_base_agent.py           ← Base AI agent class
└── simple_storage.py            ← CSV/JSON storage

Data:
├── definitive_healthcare_data.csv  ← 10,283 contacts
└── campaign_tracking.json          ← Email tracking (auto-created)

Legacy (Keep but ignore):
├── main.py                         ← Old Cloud Run entry (broken)
├── production_system.py            ← Old Firestore version (broken)
├── firestore_service.py            ← Old database (broken)
├── coordinator_agent.py            ← Old Vertex AI version (broken)
└── [50+ other old files]           ← Ignore these
```

## Daily Automation (OPTIONAL):

If you want to restore the daily automation:

```bash
# Edit crontab
crontab -e

# Change the line to:
0 9 * * * cd /Users/merandafreiner/gfmd_swarm_agent && export GROQ_API_KEY="your_key" && /usr/bin/python3 run_campaign.py 50 send >> logs/cron.log 2>&1

# This will send 50 emails every day at 9 AM
```

## Troubleshooting:

**"GROQ_API_KEY not set"**
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

**"Gmail authentication failed"**
- Your token expired. Run any command and it will auto-refresh.

**"No contacts available"**
- All 10,283 contacts were contacted in last 30 days
- Wait 30 days or edit `simple_storage.py` to change the interval

## What's Different from Before:

| Feature | Old System | New System |
|---------|-----------|------------|
| AI Provider | Vertex AI (broken) | Groq (working) |
| Database | Firestore (broken) | CSV/JSON (working) |
| Deployment | Cloud Run (complex) | Local (simple) |
| Dependencies | 25+ packages | 5 packages |
| Setup Time | Hours | 30 seconds |
| Permissions | IAM hell | None needed |
| Cost per email | Unknown | $0.0016 |
| Speed | Slow | Blazing fast |

## Next Steps:

1. **Test more**: `python3 run_campaign.py 10`
2. **Send for real**: `python3 run_campaign.py 50 send`
3. **Monitor**: Check `campaign_tracking.json`
4. **Adjust scoring**: Edit qualification thresholds in agents
5. **Customize emails**: Edit email composer agent prompts

---

**Bottom Line**: You now have a working, simple, fast B2B outreach system with zero Google Cloud dependencies. Just run the command and it works.
