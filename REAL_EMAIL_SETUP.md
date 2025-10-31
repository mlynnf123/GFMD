# Real Email Contact Setup Guide

## 🚨 CRITICAL: System Must Use Real Emails Only

The system was sending emails to fake addresses like "mail2@example.com". This guide ensures we only use verified, real email addresses.

## 1. Data Sources for Real Contacts

### A. Definitive Healthcare Sheet
- **Required**: Upload your Definitive Healthcare data export
- **Format**: CSV with columns: Organization, Contact Name, Title, Email, Phone
- **Location**: Save as `definitive_healthcare_data.csv` in project root

### B. Web Search Integration
The system needs to search for real contacts using:
- Google Custom Search API
- LinkedIn Sales Navigator API  
- Hospital website scraping
- Healthcare directories

### C. Manual Verified Contacts
Maintain a database of manually verified contacts in `verified_contacts.json`

## 2. Email Validation Requirements

Before sending ANY email, the system must verify:

1. **Domain Validation**: Email domain must be a real hospital/healthcare domain
2. **Format Check**: Proper email format (not generic like mail2@)
3. **Existence Verification**: Check if email actually exists
4. **No Placeholders**: Reject emails like "labdirector@hospital.org"

## 3. Implementation Steps

### Step 1: Load Definitive Healthcare Data
```python
# In production_rag_a2a_system.py
def load_definitive_healthcare():
    df = pd.read_csv('definitive_healthcare_data.csv')
    return df[['Organization', 'Contact_Name', 'Title', 'Email']].to_dict('records')
```

### Step 2: Web Search for Contacts
```python
# Use WebSearch tool to find real emails
search_query = f'"{hospital_name}" laboratory director email contact 2024'
results = await web_search(search_query)
```

### Step 3: Validate Before Sending
```python
# Never send to unverified emails
if not is_verified_email(prospect['email']):
    print("❌ Skipping - unverified email")
    return
```

## 4. Temporary Workaround

Until full integration is complete:

1. **Manual Contact List**: Create a CSV with verified contacts:
   ```csv
   Organization,Contact_Name,Title,Email,Verified
   Houston Methodist,Dr. John Smith,Lab Director,jsmith@houstonmethodist.org,Yes
   ```

2. **Use Only Verified**: Only process prospects with Verified=Yes

3. **No Fake Generation**: NEVER generate fake emails

## 5. Testing Real Emails

Before going live:
1. Send test emails to your own address first
2. Verify all recipient addresses are real
3. Check bounce rates and delivery status
4. Monitor for any "Address not found" errors

## 6. Google Sheets Integration

The "Sent Emails" sheet should track:
- Timestamp
- Recipient Email (must be real)
- Delivery Status
- Bounce/Error Messages

## 7. Daily Automation Changes

Modify daily automation to:
1. Load only verified contacts
2. Skip any without real emails
3. Log skipped prospects
4. Report real email percentage

## ⚠️ IMPORTANT

**NEVER** send emails to:
- Generated addresses (fake@example.com)
- Placeholder addresses (labdirector@hospital.org)  
- Unverified addresses
- Generic addresses without specific recipient

Only send to:
- ✅ Verified individual email addresses
- ✅ Contacts from Definitive Healthcare
- ✅ Manually researched and confirmed emails
- ✅ Emails found via legitimate web search