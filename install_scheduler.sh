#!/bin/bash
"""
GFMD Swarm Agent Scheduler Installation Script
Sets up daily execution at 9am CST via cron job
"""

set -e

echo "🚀 GFMD Swarm Agent Scheduler Installation"
echo "=========================================="

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_PATH=$(which python3)
SCHEDULER_SCRIPT="$SCRIPT_DIR/daily_scheduler.py"

echo "📂 Installation directory: $SCRIPT_DIR"
echo "🐍 Python path: $PYTHON_PATH"

# Install required Python packages
echo "📦 Installing required packages..."
pip3 install schedule pytz

# Make the scheduler script executable
chmod +x "$SCHEDULER_SCRIPT"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Create wrapper script for cron
WRAPPER_SCRIPT="$SCRIPT_DIR/run_daily_agents.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# GFMD Daily Agent Execution Wrapper
# This script is called by cron to run the daily agents

# Set environment variables
export PATH=/usr/local/bin:/usr/bin:/bin
export PYTHONPATH="$SCRIPT_DIR:\$PYTHONPATH"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the daily scheduler with immediate execution
$PYTHON_PATH "$SCHEDULER_SCRIPT" --run-now >> "$SCRIPT_DIR/logs/cron_execution.log" 2>&1
EOF

chmod +x "$WRAPPER_SCRIPT"

# Create cron entry (9am CST = 15:00 UTC, but we'll use system local time assuming CST)
CRON_ENTRY="0 9 * * * $WRAPPER_SCRIPT"

echo "⏰ Setting up cron job for daily execution at 9:00 AM..."

# Add cron job (check if it already exists first)
(crontab -l 2>/dev/null | grep -v "$WRAPPER_SCRIPT" || true; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron job installed successfully!"
echo "📅 The agents will now run daily at 9:00 AM"

# Show current cron jobs
echo ""
echo "📋 Current cron jobs:"
crontab -l | grep -E "(run_daily_agents|daily_scheduler)" || echo "   (No GFMD agent cron jobs found - this might indicate an issue)"

echo ""
echo "🔧 Manual execution options:"
echo "   Test run now:     python3 $SCHEDULER_SCRIPT --run-now"
echo "   Start scheduler:  python3 $SCHEDULER_SCRIPT"
echo "   View logs:        tail -f $SCRIPT_DIR/logs/daily_scheduler_$(date +%Y%m%d).log"

echo ""
echo "🎯 Setup complete! Your agents will run automatically at 9am daily."
echo "📊 All results will be exported to your Google Sheets automatically."

# Test the installation
echo ""
echo "🧪 Testing installation..."
if python3 -c "import schedule; print('✅ schedule package available')"; then
    echo "✅ Python dependencies OK"
else
    echo "❌ Python dependencies missing - please install with: pip3 install schedule pytz"
    exit 1
fi

if [ -f "$SCHEDULER_SCRIPT" ]; then
    echo "✅ Scheduler script exists"
else
    echo "❌ Scheduler script missing"
    exit 1
fi

if [ -x "$WRAPPER_SCRIPT" ]; then
    echo "✅ Wrapper script executable"
else
    echo "❌ Wrapper script not executable"
    exit 1
fi

echo ""
echo "🎉 Installation complete and verified!"
echo "💡 Run 'python3 daily_scheduler.py --run-now' to test immediately"