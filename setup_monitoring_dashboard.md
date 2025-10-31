# 📊 GFMD AI Swarm Agent - Monitoring Dashboard Setup Guide

## 🎯 Dashboard URL
Your dashboard: https://console.cloud.google.com/monitoring/dashboards/builder/7b24e670-39ce-4e95-9572-1e1285fb2892?project=windy-tiger-471523-m5

## 📈 Step-by-Step Setup Instructions

### 1. **Cloud Run Metrics** (Top Left Widget)
**Purpose**: Track daily email volume and request patterns

1. Click "Add Chart" → "Line Chart"
2. **Resource & Metric**:
   - Resource Type: `Cloud Run Revision`
   - Metric: `Request count`
3. **Filters**:
   - Add filter: `service_name = gfmd-a2a-swarm-agent`
4. **Configuration**:
   - Title: "Daily Email Volume"
   - Alignment: 1 minute
   - Aggregation: Sum

---

### 2. **Email Success Rate** (Top Right Widget)
**Purpose**: Monitor email delivery success percentage

1. Click "Add Chart" → "Scorecard"
2. **Custom Metric Setup**:
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="gfmd-a2a-swarm-agent"
   metric.labels.status="success"
   ```
3. **Thresholds**:
   - Green: > 95%
   - Yellow: 90-95%
   - Red: < 90%

---

### 3. **Processing Time** (Middle Left Widget)
**Purpose**: Monitor agent processing performance

1. Click "Add Chart" → "Line Chart"
2. **Resource & Metric**:
   - Resource Type: `Cloud Run Revision`
   - Metric: `Request latencies`
3. **Filters**:
   - Add filter: `service_name = gfmd-a2a-swarm-agent`
4. **Configuration**:
   - Title: "Agent Processing Time"
   - Show 95th percentile
   - Target line at 180 seconds (3 minutes)

---

### 4. **Memory Usage** (Middle Center Widget)
**Purpose**: Track memory consumption

1. Click "Add Chart" → "Line Chart"
2. **Resource & Metric**:
   - Resource Type: `Cloud Run Revision`
   - Metric: `Container Memory Utilization`
3. **Filters**:
   - Add filter: `service_name = gfmd-a2a-swarm-agent`
4. **Configuration**:
   - Title: "Memory Usage"
   - Alert threshold at 80%

---

### 5. **CPU Usage** (Middle Right Widget)
**Purpose**: Monitor CPU performance

1. Click "Add Chart" → "Line Chart"
2. **Resource & Metric**:
   - Resource Type: `Cloud Run Revision`
   - Metric: `Container CPU Utilization`
3. **Filters**:
   - Add filter: `service_name = gfmd-a2a-swarm-agent`

---

### 6. **Error Rate** (Bottom Left Widget)
**Purpose**: Track system errors and failures

1. Click "Add Chart" → "Line Chart"
2. **Log-based Metric**:
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="gfmd-a2a-swarm-agent"
   severity=ERROR
   ```
3. **Configuration**:
   - Title: "Error Rate"
   - Show count per minute

---

### 7. **API Quota Usage** (Bottom Right Widget)
**Purpose**: Monitor Google API consumption

1. Click "Add Chart" → "Stacked Area Chart"
2. **Add Multiple Metrics**:
   - Gmail API quota usage
   - Sheets API quota usage
   - Custom Search API quota usage
3. **Configuration**:
   - Show as percentage of quota

---

### 8. **Recent Activity Log** (Bottom Widget)
**Purpose**: Real-time activity monitoring

1. Click "Add Chart" → "Logs Panel"
2. **Log Query**:
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="gfmd-a2a-swarm-agent"
   ("Email sent successfully" OR "Processing" OR "Error")
   ```

---

## 🚨 Alert Configuration

### **Critical Alerts to Set Up:**

1. **Email Failure Alert**
   - Condition: Error rate > 10% for 5 minutes
   - Notification: Email/SMS

2. **Service Down Alert**
   - Condition: No requests for 10 minutes during business hours
   - Notification: Immediate

3. **High Latency Alert**
   - Condition: Processing time > 5 minutes
   - Notification: Email

4. **Low Daily Volume Alert**
   - Condition: Daily emails < 30 by 12 PM CST
   - Notification: Email

---

## 📱 Mobile Access

Access your dashboard on mobile:
https://console.cloud.google.com/m/monitoring/dashboards/custom/7b24e670-39ce-4e95-9572-1e1285fb2892

---

## 🎯 Key Metrics to Watch

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Email Success Rate | 95%+ | < 90% |
| Processing Time | < 3 min | > 5 min |
| Daily Email Count | 50+ | < 30 |
| Memory Usage | < 60% | > 80% |
| Error Rate | < 5% | > 10% |

---

## 💡 Pro Tips

1. **Save Dashboard**: Click "Save" and name it "GFMD AI Swarm Production"
2. **Share Access**: Click "Share" to give team members view access
3. **Export Data**: Use "Download CSV" for reporting
4. **Time Range**: Set to "Last 7 days" for trend analysis
5. **Auto-Refresh**: Enable 1-minute auto-refresh for real-time monitoring

---

## 🔧 Custom Metrics (Optional)

To track business-specific metrics, create log-based metrics:

1. **Qualification Score Distribution**
   ```
   textPayload=~"Qualification score: ([0-9]+)"
   ```

2. **Contact Source Tracking**
   ```
   jsonPayload.source="definitive_healthcare" OR jsonPayload.source="google_search"
   ```

3. **Agent Performance**
   ```
   jsonPayload.agent_type="research" AND jsonPayload.processing_time
   ```

---

## 📞 Support

- **Dashboard Issues**: Check Cloud Monitoring documentation
- **Metric Missing**: Ensure Cloud Run service is active
- **No Data**: Verify service name is exactly "gfmd-a2a-swarm-agent"