#!/bin/bash
# Dashboard Rebuild Plan - Execute this to clean up and start fresh

echo "🧹 DASHBOARD CLEANUP & REBUILD PLAN"
echo "===================================="
echo ""
echo "This will:"
echo "  1. Backup current dashboard"
echo "  2. Remove old components (built for Firestore/Vertex AI)"
echo "  3. Keep Next.js structure"
echo "  4. Prepare for new Groq-powered components"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

cd dashboard

echo ""
echo "📦 Step 1: Backing up current dashboard..."
cp -r . ../dashboard_backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created: ../dashboard_backup_*"

echo ""
echo "🗑️  Step 2: Removing old components..."
# Remove old component files (keep UI library)
rm -f components/dashboard-page.tsx
rm -f components/real-time-dashboard.tsx
rm -f components/simplified-dashboard.tsx
echo "✅ Removed old components"

echo ""
echo "🗑️  Step 3: Removing old page files..."
# Remove old pages (we'll rebuild these)
rm -rf app/agents
rm -rf app/leads
rm -rf app/opportunities
echo "✅ Removed old pages"

echo ""
echo "🗑️  Step 4: Cleaning up temp files..."
rm -f debug-contacts.ts
rm -f fix-import.js
rm -f import-contacts-direct.ts
rm -f import-csv-data.js
rm -f quick-import.js
rm -f test-contacts.csv
rm -f mock-data.json
rm -f temp_*.csv
echo "✅ Cleaned temp files"

echo ""
echo "✅ Dashboard cleaned!"
echo ""
echo "📝 Next steps:"
echo "  1. We'll create new API backend (Flask)"
echo "  2. Build new React components for:"
echo "     - Overview/Dashboard"
echo "     - Campaigns (run campaigns)"
echo "     - Contacts (browse 10K contacts)"
echo "     - Logs (real-time)"
echo "     - Analytics (charts)"
echo "     - Settings"
echo ""
echo "Ready to build the new dashboard!"
