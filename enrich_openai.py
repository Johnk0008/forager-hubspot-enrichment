import os
import requests
from dotenv import load_dotenv

from pathlib import Path
from dotenv import load_dotenv
import os

# Explicitly specify the .env path relative to the script's location
env_path = Path(__file__).resolve().parent / ".env"
print("Loading .env from:", env_path)  # For debugging, verify the path is correct
load_dotenv(dotenv_path=env_path, override=True)

FORAGER_KEY = os.getenv("FORAGER_API_KEY")
FORAGER_ACCOUNT = os.getenv("FORAGER_ACCOUNT_ID")
print("FORAGER_ACCOUNT_ID =", os.getenv("FORAGER_ACCOUNT_ID"))
HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")

FORAGER_BASE = f"https://api-v2.forager.ai/api/{FORAGER_ACCOUNT}/datastorage"
HUBSPOT_BASE = "https://api.hubapi.com"

# --- 1. Fetch complete OpenAI company data from Forager ---
def get_openai_company():
    resp = requests.post(
        f"{FORAGER_BASE}/organization_search/",
        headers={"X-API-KEY": FORAGER_KEY, "Content-Type": "application/json"},
        json={"linkedin_public_identifiers": ["openai"]},
    )
    if resp.status_code not in (200, 201):
       print("HubSpot error:", resp.text)
    resp.raise_for_status()
    return resp.json()["search_results"][0]

# --- 2. Create/Update company in HubSpot ---
def upsert_hubspot_company(company):
    props = {
        "name": company["name"],
        "domain": company["domain"],
        "description": company.get("description") or "",
        "annualrevenue": str(company.get("finance_info", {}).get("revenue", "")) if company.get("finance_info") else "",
        "numberofemployees": str(company.get("employees_amount") or ""),
        "linkedin_company_page": company.get("linkedin_info", {}).get("public_profile_url", ""),
        "city": (company.get("addresses") or [{}])[0].get("city", "") if company.get("addresses") else "",
        "state": (company.get("addresses") or [{}])[0].get("state", "") if company.get("addresses") else "",
        "country": (company.get("addresses") or [{}])[0].get("country", "") if company.get("addresses") else "",
    }
    # First search by domain
    search = requests.post(
        f"{HUBSPOT_BASE}/crm/v3/objects/companies/search",
        headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"},
        json={"filterGroups": [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": company["domain"]}]}]},
    )
    results = search.json().get("results", [])
    if results:
        cid = results[0]["id"]
        requests.patch(
            f"{HUBSPOT_BASE}/crm/v3/objects/companies/{cid}",
            headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"},
            json={"properties": props},
        )
        return cid
    resp = requests.post(
        f"{HUBSPOT_BASE}/crm/v3/objects/companies",
        headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"},
        json={"properties": props},
    )
    if resp.status_code not in (200, 201):
       print("HubSpot error:", resp.text)
    resp.raise_for_status()
    return resp.json()["id"]

# --- 3. Create/Update contact in HubSpot ---
def upsert_hubspot_contact(person):
    props = {
        "firstname": person["first_name"],
        "lastname": person["last_name"],
        "email": person["email"],
        "phone": person.get("phone", ""),
        "jobtitle": person["role_title"],
        "city": (person.get("location") or {}).get("name", "").split(",")[0].strip() if person.get("location") else "",
        "state": "",
        "country": "",
    }
    # Extract city/state/country from location
    if person.get("location"):
        parts = [p.strip() for p in person["location"]["name"].split(",")]
        if len(parts) >= 1: props["city"] = parts[0]
        if len(parts) >= 2: props["state"] = parts[1]
        if len(parts) >= 3: props["country"] = parts[2]

    # Search by email
    search = requests.post(
        f"{HUBSPOT_BASE}/crm/v3/objects/contacts/search",
        headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"},
        json={"filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": person["email"]}]}]},
    )
    results = search.json().get("results", [])
    if results:
        cid = results[0]["id"]
        requests.patch(
            f"{HUBSPOT_BASE}/crm/v3/objects/contacts/{cid}",
            headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"},
            json={"properties": props},
        )
        return cid
    resp = requests.post(
        f"{HUBSPOT_BASE}/crm/v3/objects/contacts",
        headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"},
        json={"properties": props},
    )
    if resp.status_code not in (200, 201):
       print("HubSpot error:", resp.text)
    return resp.json()["id"]

# --- 4. Associate Contact and Company ---
def associate(contact_id, company_id):
    requests.put(
        f"{HUBSPOT_BASE}/crm/v3/objects/contacts/{contact_id}/associations/companies/{company_id}/contact_to_company",
        headers={"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"},
    )

# --- Main Process ---
if __name__ == "__main__":
    print("Fetching OpenAI company data from Forager...")
    company = get_openai_company()
    print(f"Company retrieved: {company['name']}, revenue={company.get('finance_info')}")

    print("Writing company to HubSpot...")
    company_id = upsert_hubspot_company(company)
    print(f"Company ID: {company_id}")

    # Data for 5 people (from your Forager results)
    people = [
        {"first_name": "Kristen", "last_name": "Pawloski", "email": "kristenpaw24@gmail.com", "phone": "+16507935261", "role_title": "Technical Recruiter", "headline": "Technical Recruiter @ OpenAI", "linkedin_info": {"public_profile_url": "https://www.linkedin.com/in/kjpawloski/"}, "location": {"name": "san francisco, california, united states"}},
        {"first_name": "Holly", "last_name": "Blake", "email": "hols.blake@gmail.com", "phone": "+353838251600", "role_title": "Founding Recruiter | EMEA", "headline": "Talent | OpenAI | Love to build", "linkedin_info": {"public_profile_url": "https://www.linkedin.com/in/holly-blake-64409a49/"}, "location": {"name": "san francisco bay, united states"}},
        {"first_name": "Stella", "last_name": "L.", "email": "sweetstella84@hotmail.com", "phone": "+12013540803", "role_title": "Senior Technical Recruiter", "headline": "Technical IT Recruiter", "linkedin_info": {"public_profile_url": "https://www.linkedin.com/in/ella-recruiter/"}, "location": {"name": "bergenfield, new jersey, united states"}},
        {"first_name": "Phuong", "last_name": "Vu", "email": "phuong.voo@gmail.com", "phone": "+14089311400", "role_title": "Recruiter", "headline": "Recruiting", "linkedin_info": {"public_profile_url": "https://www.linkedin.com/in/phuongvu/"}, "location": {"name": "united states"}},
        {"first_name": "Keegan", "last_name": "Y.", "email": "entirix@gmail.com", "phone": "", "role_title": "Founding Recruiter (Former OpenAI)", "headline": "Founding Recruiter at Gumloop | Former OpenAI", "linkedin_info": {"public_profile_url": "https://www.linkedin.com/in/dkyv/"}, "location": {"name": "san francisco, california, united states"}},
    ]

    for p in people:
        print(f"Writing contact to HubSpot: {p['first_name']} {p['last_name']}")
        cid = upsert_hubspot_contact(p)
        associate(cid, company_id)
        print(f"  ✅ Contact ID: {cid}, associated with company")

    print("\n🎉 Done! Check HubSpot for the OpenAI company + 5 contacts.")