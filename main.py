import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")

FORAGER_KEY = os.getenv("FORAGER_API_KEY")
FORAGER_ACCOUNT = os.getenv("FORAGER_ACCOUNT_ID")
HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
FORAGER_BASE = f"https://api-v2.forager.ai/api/{FORAGER_ACCOUNT}/datastorage"
HUBSPOT_BASE = "https://api.hubapi.com"

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/webhook/company-created")
async def company_created(request: Request):
    payload = await request.json()
    print("=== Webhook received! ===", payload)
    
    events = payload if isinstance(payload, list) else [payload]
    for ev in events:
        company_id = ev.get("objectId")
        if not company_id:
            continue
        
        # HubSpot से कंपनी का डोमेन प्राप्त करें
        r = requests.get(
            f"{HUBSPOT_BASE}/crm/v3/objects/companies/{company_id}",
            headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}"},
            params={"properties": "domain,name"},
        )
        if r.status_code != 200:
            print("HubSpot company fetch failed:", r.text)
            continue
            
        company = r.json().get("properties", {})
        domain = company.get("domain")
        if not domain:
            continue
            
        # Forager से कंपनी एनरिच करें
        fr = requests.post(
            f"{FORAGER_BASE}/organization_search/",
            headers={"X-API-KEY": FORAGER_KEY, "Content-Type": "application/json"},
            json={"domains": [domain]},
        )
        if fr.status_code == 200 and fr.json().get("search_results"):
            fc = fr.json()["search_results"][0]
            props = {
                "description": fc.get("description") or "",
                "annualrevenue": str(fc.get("finance_info", {}).get("revenue", "")) if fc.get("finance_info") else "",
                "numberofemployees": str(fc.get("employees_amount") or ""),
            }
            requests.patch(
                f"{HUBSPOT_BASE}/crm/v3/objects/companies/{company_id}",
                headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"},
                json={"properties": props},
            )
    return {"ok": True}