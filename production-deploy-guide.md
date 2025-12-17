# 🚀 GFMD Email Automation - Google Cloud Deployment Guide

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI** installed: [Install gcloud](https://cloud.google.com/sdk/docs/install)
3. **Project created** in Google Cloud Console
4. **Gmail API credentials** (gmail_credentials.json)

## 🔧 Quick Deployment

### Step 1: Set Your Project ID
```bash
export PROJECT_ID="your-actual-project-id"
```

### Step 2: Make Scripts Executable
```bash
chmod +x deploy.sh secrets-setup.sh
```

### Step 3: Set Up Secrets
```bash
./secrets-setup.sh
```
This will prompt you for:
- MongoDB connection string
- MongoDB password  
- Groq API key
- Gmail credentials file path

### Step 4: Deploy to Google Cloud
```bash
./deploy.sh
```

## 📊 What Gets Deployed

### **Google Cloud Run Service**
- **Service Name**: `gfmd-email-automation`
- **Region**: `us-central1` (configurable)
- **Resources**: 1 CPU, 1GB RAM
- **Scaling**: Min 1, Max 1 instance (always running)
- **Networking**: Allow unauthenticated (for health checks)

### **Service Account & Permissions**
- **Account**: `gfmd-automation-sa@PROJECT_ID.iam.gserviceaccount.com`
- **Permissions**: Secret Manager access for credentials

### **Secrets Management**
- `gfmd-mongodb-connection` - MongoDB Atlas connection string
- `gfmd-mongodb-password` - Database password
- `gfmd-groq-api-key` - Groq AI API key
- `gfmd-gmail-credentials` - Gmail API credentials JSON

## ⏰ Automated Schedule (Production)

Once deployed, the system runs **24/7** with:

### **Daily Contact Addition** 
- **Time**: 8:00 AM Monday-Friday (business days)
- **Volume**: 20 new contacts from database
- **Source**: Existing 908 contacts in MongoDB

### **Email Processing**
- **Frequency**: Every hour + special runs at 9 AM, 1 PM, 5 PM
- **Timing**: Every 2 business days between emails
- **Business Hours**: Only sends 8 AM - 6 PM on weekdays

## 📈 Expected Performance

### **Daily Volume**
- 20 new email sequences started
- 40-50 total emails sent per business day
- Professional business-day timing only

### **Cost Estimation (Google Cloud)**
- **Cloud Run**: ~$15-30/month (1 instance, always on)
- **Secrets Manager**: ~$1-2/month  
- **Container Registry**: ~$1-2/month
- **Total**: ~$20-35/month

## 🔍 Monitoring & Management

### **View Logs**
```bash
gcloud run logs tail gfmd-email-automation --region us-central1 --follow
```

### **Check Service Status**
```bash
gcloud run services describe gfmd-email-automation --region us-central1
```

### **Update Secrets**
```bash
# Update any secret
echo "new-value" | gcloud secrets versions add gfmd-groq-api-key --data-file=-
```

### **Redeploy Service**
```bash
# After code changes
./deploy.sh
```

## 🛠️ Manual Commands

### **Add Contacts Manually**
```bash
gcloud run services proxy gfmd-email-automation --port 8080 &
curl -X POST "http://localhost:8080/add_contacts?count=20"
```

### **Check Statistics**
```bash
curl "http://localhost:8080/stats"
```

## 🔒 Security Features

### **Environment Security**
- All secrets stored in Google Secret Manager
- Service account with minimal required permissions
- Container runs as non-root user
- No secrets in container image or code

### **Network Security**
- HTTPS-only communication
- Google Cloud VPC networking
- IAM-based access controls

## 🚨 Troubleshooting

### **Common Issues**

#### 1. **Deployment Fails**
```bash
# Check if APIs are enabled
gcloud services list --enabled

# Check permissions
gcloud projects get-iam-policy $PROJECT_ID
```

#### 2. **Service Won't Start**
```bash
# Check logs for errors
gcloud run logs tail gfmd-email-automation --region us-central1

# Verify secrets exist
gcloud secrets list --filter="name~gfmd-"
```

#### 3. **MongoDB Connection Issues**
```bash
# Test MongoDB connection locally first
python3 -c "from mongodb_storage import MongoDBStorage; MongoDBStorage()"
```

#### 4. **Gmail Authentication Problems**
```bash
# Re-upload Gmail credentials
gcloud secrets versions add gfmd-gmail-credentials --data-file=gmail_credentials.json
```

## 🎯 Production Checklist

- [ ] Project ID set correctly
- [ ] All secrets created and accessible
- [ ] Gmail API credentials working
- [ ] MongoDB connection tested
- [ ] Groq API key valid
- [ ] Service deployed successfully
- [ ] Logs showing successful startup
- [ ] First scheduled run completed
- [ ] Email sending verified

## 📞 Support

### **View Service URL**
```bash
gcloud run services describe gfmd-email-automation --region us-central1 --format="value(status.url)"
```

### **Scale Service** 
```bash
# Temporarily stop (min instances = 0)
gcloud run services update gfmd-email-automation --region us-central1 --min-instances 0

# Resume (min instances = 1)  
gcloud run services update gfmd-email-automation --region us-central1 --min-instances 1
```

## 🎉 Success!

Once deployed, your GFMD email automation will:
- ✅ Run continuously on Google Cloud
- ✅ Add 20 contacts daily from your database
- ✅ Send personalized, RAG-enhanced emails
- ✅ Follow business day scheduling
- ✅ Scale automatically with demand
- ✅ Provide detailed logging and monitoring

Your email sequences are now fully automated and production-ready!