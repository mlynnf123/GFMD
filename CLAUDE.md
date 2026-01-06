# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GFMD AI Swarm Agent System - A high-performance, multi-agent AI system for automated B2B sales outreach to law enforcement agencies using Groq AI and MongoDB storage.

## Design Guidelines

- For styling, NO EMOJIS or icons
- Use only white, black, grey, and light blue for colors
- All fonts must have a weight of 400 or less (400 for headings)

## Development Commands

### Quick Start
```bash
# Set Groq API key (required)
export GROQ_API_KEY="your_key_here"

# Test with 5 prospects (dry run - doesn't send emails)
python3 run_campaign.py 5

# Actually send 50 emails
python3 run_campaign.py 50 send
```

## Deployment Notes

- No we are supposed to be using the railway CLI not github to deploy
- We are deploying using the CLI not github
- We use the Mongodb extension in VS Code as well