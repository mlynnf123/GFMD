# 🎯 GFMD AI Swarm - Vertex AI Dashboard Setup Guide

## 📍 Your Dashboard Location
**Direct Link**: https://console.cloud.google.com/monitoring/dashboards/builder/7b24e670-39ce-4e95-9572-1e1285fb2892?project=windy-tiger-471523-m5

---

## 🚀 STEP-BY-STEP WIDGET SETUP

### **Widget 1: Daily Email Volume** 
**Purpose**: Track how many emails your system sends daily

1. **Click "Add Chart"** (+ button)
2. **Select "Line Chart"**
3. **In Metrics Explorer**:
   - **Resource**: Cloud Run Revision
   - **Metric**: Request count  
   - **Filter**: Add filter → `service_name` = `gfmd-a2a-swarm-agent`
   - **Group By**: Leave empty
   - **Aggregation**: Sum
4. **Title**: "Daily Email Volume"
5. **Click "Apply"**

---

### **Widget 2: Processing Time**
**Purpose**: Monitor how long it takes to process each prospect

1. **Click "Add Chart"** (+ button)
2. **Select "Line Chart"**
3. **In Metrics Explorer**:
   - **Resource**: Cloud Run Revision
   - **Metric**: Request latencies
   - **Filter**: Add filter → `service_name` = `gfmd-a2a-swarm-agent`
   - **Aggregation**: 95th percentile
4. **Title**: "Agent Processing Time"
5. **Add threshold line at 300 seconds (5 minutes)**
6. **Click "Apply"**

---

### **Widget 3: Memory Usage**
**Purpose**: Monitor system memory consumption

1. **Click "Add Chart"** (+ button)
2. **Select "Line Chart"**
3. **In Metrics Explorer**:
   - **Resource**: Cloud Run Revision
   - **Metric**: Container memory utilizations
   - **Filter**: Add filter → `service_name` = `gfmd-a2a-swarm-agent`
   - **Aggregation**: Mean
4. **Title**: "Memory Usage"
5. **Add threshold line at 80%**
6. **Click "Apply"**

---

### **Widget 4: CPU Usage**
**Purpose**: Track CPU performance

1. **Click "Add Chart"** (+ button)
2. **Select "Line Chart"**
3. **In Metrics Explorer**:
   - **Resource**: Cloud Run Revision
   - **Metric**: Container CPU utilizations
   - **Filter**: Add filter → `service_name` = `gfmd-a2a-swarm-agent`
   - **Aggregation**: Mean
4. **Title**: "CPU Usage"
5. **Click "Apply"**

---

### **Widget 5: Error Rate**
**Purpose**: Track system errors and failures

1. **Click "Add Chart"** (+ button)
2. **Select "Line Chart"**
3. **In Metrics Explorer**:
   - **Resource**: Cloud Run Revision
   - **Metric**: Request count
   - **Filter**: Add two filters:
     - `service_name` = `gfmd-a2a-swarm-agent`
     - `response_code_class` ≠ `2xx`
   - **Aggregation**: Rate
4. **Title**: "Error Rate"
5. **Click "Apply"**

---

### **Widget 6: Recent Activity Logs**
**Purpose**: See real-time system activity

1. **Click "Add Chart"** (+ button)
2. **Select "Logs Panel"**
3. **Log Query** (copy exactly):
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="gfmd-a2a-swarm-agent"
   ("Email sent successfully" OR "Processing" OR "Error" OR "Failed")
   ```
4. **Title**: "Recent Activity"
5. **Click "Apply"**

---

## 🚨 CRITICAL ALERTS SETUP

### **Alert 1: Email Failure Rate**
1. **Go to**: https://console.cloud.google.com/monitoring/alerting?project=windy-tiger-471523-m5
2. **Click "Create Policy"**
3. **Condition**:
   - Resource: Cloud Run Revision
   - Metric: Your custom email failure metric
   - Threshold: > 10%
   - Duration: 5 minutes
4. **Notification**: Add your email
5. **Name**: "GFMD - High Email Failure Rate"

### **Alert 2: Service Downtime**
1. **Create Policy**
2. **Condition**:
   - Resource: Cloud Run Revision  
   - Metric: Request count
   - Threshold: = 0 requests
   - Duration: 10 minutes
   - Time restriction: 8 AM - 6 PM CST
3. **Notification**: Immediate (SMS + Email)
4. **Name**: "GFMD - Service Down"

### **Alert 3: High Processing Time**
1. **Create Policy**
2. **Condition**:
   - Resource: Cloud Run Revision
   - Metric: Request latencies
   - Threshold: > 300 seconds (5 minutes)
   - Duration: 3 minutes
3. **Notification**: Email
4. **Name**: "GFMD - Slow Processing"

---

## 📱 MOBILE ACCESS SETUP

1. **Download Google Cloud Console app**
2. **Login with your account**
3. **Select project**: windy-tiger-471523-m5
4. **Navigate to**: Monitoring → Dashboards
5. **Find**: GFMD AI Swarm Dashboard
6. **Enable push notifications**

---

## 🎯 BUSINESS METRICS TO TRACK

### **Key Performance Indicators:**

| Metric | Target | Current Status |
|--------|--------|----------------|
| **Daily Emails** | 50+ | ✅ 20/20 success |
| **Success Rate** | 95%+ | ✅ 100% |
| **Processing Time** | < 3 min | ✅ ~2-3 min |
| **Memory Usage** | < 60% | ✅ Normal |
| **Uptime** | 99%+ | ✅ Active |

### **Business Value Tracking:**
- **Contact Quality**: Only real healthcare professionals
- **Personalization**: AI-crafted unique messages
- **Automation**: Zero manual intervention
- **Scalability**: Ready for 50+ daily emails

---

## 🔧 TROUBLESHOOTING

### **No Data Showing?**
1. Verify service name is exactly: `gfmd-a2a-swarm-agent`
2. Check time range (set to "Last 24 hours")
3. Ensure Cloud Run service is active

### **Alerts Not Firing?**
1. Test condition manually
2. Check notification channels
3. Verify alert policy is enabled

### **Dashboard Loading Slowly?**
1. Reduce time range
2. Limit widgets to essential metrics
3. Use 1-minute alignment for real-time data

---

## 📊 ADVANCED FEATURES

### **Custom Log-Based Metrics:**
Create these for business-specific tracking:

1. **Email Success Rate**:
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="gfmd-a2a-swarm-agent"
   textPayload=~"Email sent successfully"
   ```

2. **Prospect Processing Count**:
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="gfmd-a2a-swarm-agent"
   textPayload=~"Processing.*prospect"
   ```

### **Dashboard Sharing:**
1. Click "Share" in dashboard
2. Add team members with "Viewer" role
3. Generate public link for stakeholders

---

## ✅ SETUP COMPLETION CHECKLIST

- [ ] All 6 core widgets added and configured
- [ ] 3 critical alerts set up with notifications
- [ ] Mobile access configured
- [ ] Team members added with appropriate permissions
- [ ] Custom business metrics created
- [ ] Dashboard saved and named appropriately
- [ ] Test run completed to verify all metrics working

---

**🎉 Your GFMD AI Swarm monitoring dashboard is now enterprise-ready with real-time visibility into system performance, email delivery success, and automated alerting for any issues!**