#!/bin/bash
# GFMD Daily Agent Execution Wrapper
# This script is called by cron to run the daily agents

# Set environment variables
export PATH=/usr/local/bin:/usr/bin:/bin
export PYTHONPATH="/Users/merandafreiner/gfmd_swarm_agent:$PYTHONPATH"

# Change to the script directory
cd "/Users/merandafreiner/gfmd_swarm_agent"

# Run the daily scheduler with immediate execution
/usr/bin/python3 "/Users/merandafreiner/gfmd_swarm_agent/daily_scheduler.py" --run-now >> "/Users/merandafreiner/gfmd_swarm_agent/logs/cron_execution.log" 2>&1
