
***

```markdown
# Forager x HubSpot Enrichment Automation

## 📌 Project Overview
This project is a custom-built Python automation that connects **Forager** (a data enrichment tool) with **HubSpot** (CRM). It is designed to automatically enrich company and contact records, and includes a live webhook listener to handle real-time data enrichment when new records are created in HubSpot.

This solution is built as a FastAPI web service, deployed on Railway, and strictly uses custom Python code (no low-code/no-code tools like n8n).

## 🔗 Live Links
- **Live API Health Check:** [https://forager-hubspot-enrichment-production.up.railway.app/health](https://forager-hubspot-enrichment-production.up.railway.app/health)
- **GitHub Repository:** [https://github.com/Johnk0008/forager-hubspot-enrichment](https://github.com/Johnk0008/forager-hubspot-enrichment)

## 🚀 Features Implemented
1. **Company Enrichment:** Fetches full company details (description, revenue, headcount, domain, LinkedIn URL, etc.) from Forager and updates the HubSpot company record.
2. **Contact Enrichment:** Enriches contacts with names, job titles, phone numbers, locations (city, state, country), and emails.
3. **Job Title Filtering:** Utilizes Forager's `person_role_search` API to filter and discover contacts based on specific job titles (e.g., "Recruiter", "Engineer").
4. **Company Webhook Automation:** When a new company is created in HubSpot, a webhook triggers our FastAPI service. The service fetches the company's domain, gets full details from Forager, and updates the HubSpot record automatically.
5. **Secure Environment Variables:** All sensitive API keys (Forager API Key, HubSpot Service Key) are stored securely as environment variables on Railway and locally in a `.env` file (excluded from Git).

## 🛠️ Tech Stack
- **Language:** Python 3
- **Framework:** FastAPI, Uvicorn
- **Deployment:** Railway
- **Integrations:** Forager API, HubSpot CRM API, HubSpot Project-based App (Webhooks)
- **Libraries:** `requests`, `python-dotenv`, `fastapi`, `uvicorn`

## 📊 Primary Deliverable: OpenAI Demo Records
As requested in the assignment, the following records have been successfully enriched and populated in HubSpot:
- **Company:** **OpenAI** (Full details including description, revenue (1.6B), headcount (10,480), domain, and LinkedIn URL).
- **Contacts:** 5 employees from OpenAI under this company. Each contact includes First Name, Last Name, Job Title, Location (City, State, Country), Phone Number, and Email.

### ⚠️ Important Note on Emails (For Discussion)
During the evaluation, it was observed that **Forager's coverage for corporate/work emails at large tech enterprises like OpenAI is extremely low** (0 work emails found across 25+ lookups). 

To fulfill the assignment requirement of providing complete contact info including emails, the enrichment script was adapted to pull **verified personal emails** (e.g., Gmail, Hotmail) using Forager's `personal_emails` endpoint. 
- All 5 contacts have verified personal emails and mobile numbers populated in HubSpot. 
- **Flag for Discussion:** Should we use personal emails for outreach in this specific use case, or implement a waterfall enrichment strategy (Forager + other tools) to find work emails for large enterprises?

### 💡 "Interesting Extra Details" surfaced by Forager (Flagged for Discussion)
Forager surfaces excellent extra data that could be added to HubSpot for better sales/marketing personalization, if approved:
- **Full LinkedIn Headline & "About" Summary:** Captures the person's narrative (e.g., "Senior AI Engineer with 10+ years of experience...").
- **Skills Array:** A comprehensive list of technical skills extracted from their profile (e.g., Python, AWS, Machine Learning).
- **Job Description:** Specific achievements listed in their current role (e.g., "Built a system to check over two ImageNets-worth of images per day...").
*(Recommendation: We can map these extra fields to custom HubSpot contact properties).*

## ⚙️ How to Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Johnk0008/forager-hubspot-enrichment.git
   cd forager-hubspot-enrichment
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory:
   ```env
   FORAGER_API_KEY=your_forager_api_key
   FORAGER_ACCOUNT_ID=your_forager_account_id
   HUBSPOT_TOKEN=your_hubspot_service_key
   ```

4. Run the bulk enrichment script (Enriches OpenAI + 5 contacts):
   ```bash
   python enrich_openai.py
   ```

5. Run the FastAPI webhook server locally:
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## 🪝 Webhook Configuration
The webhook automation is built using a HubSpot Project-based App (subscribed to `company.creation` events). 
- **Target URL:** `https://forager-hubspot-enrichment-production.up.railway.app/webhook/company-created`
- **Verification:** When a test company (e.g., "OPENAI TEST 2") was created in HubSpot, the webhook successfully triggered, and the activity log inside HubSpot shows **"Record Enriched"** (Logo URL updated via the Forager API).

---
**Author:** Johny Kumar  
**Role:** AI Automation Engineer Evaluation Task
```
