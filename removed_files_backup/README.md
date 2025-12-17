# GFMD AI Swarm Agent

**B2B Email Outreach System powered by Groq AI**

## Status: ✅ Fully Working

A high-performance, multi-agent AI system for automated B2B sales outreach to law enforcement agencies.

## Quick Start

```bash
# 1. Set your Groq API key
export GROQ_API_KEY="your_key_here"

# 2. Test with 5 prospects (dry run - doesn't send)
python3 run_campaign.py 5

# 3. Actually send 50 emails
python3 run_campaign.py 50 send
```

## What This Does

Automatically:
1. **Researches** law enforcement agencies using AI
2. **Scores** leads 0-100 (only sends to 50+)
3. **Composes** personalized, human-sounding emails
4. **Sends** via Gmail API
5. **Tracks** everything in simple JSON files

## Tech Stack

- **AI**: Groq (Llama 3.3 70B) - Blazing fast, cheap
- **Storage**: CSV + JSON files (no database needed)
- **Email**: Gmail API
- **Data**: Law enforcement contacts database

## Cost

~$0.0016 per email (Groq AI tokens)
- 100 emails: $0.16
- 1,000 emails: $1.60

## Architecture

### 3 AI Agents:
1. **Research Agent** - Analyzes agencies, finds pain points
2. **Qualification Agent** - Scores 0-100, prioritizes HIGH/MEDIUM/LOW
3. **Email Composer** - Writes personalized emails (no AI buzzwords)

### Key Files:
- `run_campaign.py` - Main script
- `groq_coordinator.py` - Orchestrates all agents
- `simple_storage.py` - CSV/JSON storage manager
- `law_enforcement_contacts.csv` - Law enforcement contacts
- `campaign_tracking.json` - Email history (auto-created)

## Documentation

- [GROQ_SYSTEM_README.md](GROQ_SYSTEM_README.md) - Full system guide
- [DASHBOARD_DESIGN.md](DASHBOARD_DESIGN.md) - Dashboard specs

## Sample Output

```
Processed: 3 prospects
Emails generated: 3
Scores: 85/100, 90/100, 90/100
Time: 30 seconds
Tokens: 8,404

Sample Email:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
To: chief.martinez@metrocitypd.gov
Subject: Evidence destruction backlog at Metro City PD

Hi Robert,

I see Metro City PD is dealing with a growing backlog of evidence destruction while keeping an eye on the budget. Our Narc Gone system lets you destroy narcotics on-site, cutting incineration costs by roughly a third.

Would you be open to a quick call to see if it could help your department?

Best,
Mark Thompson
GFMD
mark@gfmd.com
(555) 123-4567
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Features

- ✅ Multi-agent AI pipeline
- ✅ Intelligent lead qualification
- ✅ Human-sounding email generation
- ✅ 30-day re-contact prevention
- ✅ Gmail integration
- ✅ Simple file-based storage
- ✅ Zero Google Cloud dependencies
- ✅ Comprehensive logging

## Development

```bash
# Install dependencies
pip install groq flask flask-cors

# Test individual agents
python3 groq_research_agent.py
python3 groq_qualification_agent.py
python3 groq_email_composer_agent.py

# Test full pipeline
python3 groq_coordinator.py

# Start dashboard API (optional)
python3 dashboard_api.py
```

## System History

**v2.0 (Oct 2025)** - Complete rebuild
- Migrated from Vertex AI → Groq
- Migrated from Firestore → CSV/JSON
- Removed all Google Cloud dependencies
- 10x faster, 1/10th the cost

**v1.0 (Sep 2025)** - Original system
- Vertex AI + Firestore
- Had permission issues
- Last successful run: Sept 22, 2025

## License

Private - GFMD
