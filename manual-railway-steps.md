# 🚂 Manual Railway Deployment Steps

Since the CLI is having TTY issues, let's do this manually:

## 🔧 Step 1: Complete Setup in Railway Dashboard

**Open Railway Dashboard:**
1. Go to https://railway.app/dashboard
2. Find your "gfmd-email-automation" project
3. Click on it

**Add a Service:**
1. Click "Add Service" or "New Service"
2. Choose "Deploy from GitHub"
3. Connect your GitHub account if needed
4. Select the repository with your GFMD code

**OR if you prefer to deploy directly:**
1. Click "Add Service"
2. Choose "Empty Service"
3. Name it "gfmd-automation"

## 🔧 Step 2: Set Environment Variables (In Dashboard)

Go to your service → Settings → Environment Variables

Add these variables:
```
ENVIRONMENT=production
MONGODB_CONNECTION_STRING=mongodb+srv://solutions-account:GFMDgfmd2280%40%40@cluster0.hdejtab.mongodb.net/?appName=Cluster0
MONGODB_PASSWORD=GFMDgfmd2280@@
GROQ_API_KEY=your_groq_api_key_here
GMAIL_CREDENTIALS_PATH=/app/gmail_credentials.json
TOKENIZERS_PARALLELISM=false
PYTHONUNBUFFERED=1
PYTHONPATH=/app
```

## 🔧 Step 3: Deploy

Once the service is created, try the CLI again:
```bash
# Check if service is now linked
railway status

# Deploy the code
railway up --detach
```

## 🔧 Alternative: CLI Service Creation

Try this in your terminal (it might work now):
```bash
# Try linking to existing service
railway service link

# If that doesn't work, try manual deployment
railway up --service [service-name]
```

Would you like to:
1. **Use the Railway Dashboard** (recommended - easier)
2. **Keep trying CLI commands**
3. **Switch to a different platform** (Render.com is completely free)

Let me know what you'd prefer!