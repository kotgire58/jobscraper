# job_scraper.py
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

KEYWORDS = ["entry level", "software engineer", "full stack", "quant", "software", "developer", "fullstack"]
EXCLUDE_KEYWORDS = ["senior", "staff", "lead", "manager", "principal", "director", "architect"]
OUTPUT_FILE = "job_log.json"
GREENHOUSE_COMPANIES_FILE = "greenhouse_companies.json"
LEVER_COMPANIES_FILE = "lever_companies.json"

# Load dynamic company lists
with open(GREENHOUSE_COMPANIES_FILE, 'r') as f:
    GREENHOUSE_SLUGS = json.load(f)

with open(LEVER_COMPANIES_FILE, 'r') as f:
    LEVER_SLUGS = json.load(f)

def is_relevant_job(title, location):
    title = title.lower()
    location = location.lower()
    return (
        any(k in title for k in KEYWORDS)
        and not any(e in title for e in EXCLUDE_KEYWORDS)
        and "united states" in location
    )

def fetch_greenhouse_jobs(slug):
    api_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    try:
        res = requests.get(api_url, timeout=10)
        data = res.json()
        jobs = []
        for job in data.get("jobs", []):
            title = job.get("title", "")
            location = job.get("location", {}).get("name", "")
            if is_relevant_job(title, location):
                job_obj = {
                    "source": "greenhouse",
                    "title": title,
                    "company": slug,
                    "link": job.get("absolute_url"),
                    "location": location,
                    "date": datetime.utcnow().isoformat()
                }
                jobs.append(job_obj)
        return jobs
    except Exception as e:
        print(f"Error fetching Greenhouse jobs from {slug}: {e}")
        return []

def fetch_lever_jobs(slug):
    json_url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        res = requests.get(json_url, timeout=10)
        data = res.json()
        jobs = []
        if isinstance(data, list):
            for job in data:
                if isinstance(job, dict):
                    title = job.get("text", "")
                    location = job.get("categories", {}).get("location", "")
                    if is_relevant_job(title, location):
                        job_obj = {
                            "source": "lever",
                            "title": title,
                            "company": slug,
                            "link": job.get("hostedUrl"),
                            "location": location,
                            "date": datetime.utcnow().isoformat()
                        }
                        jobs.append(job_obj)
        return jobs
    except Exception as e:
        print(f"Error fetching Lever jobs from {slug}: {e}")
        return []

def is_recent(date_str):
    try:
        return datetime.now() - datetime.fromisoformat(date_str) < timedelta(days=1)
    except:
        return False

def save_jobs(jobs):
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            old_jobs = json.load(f)
    else:
        old_jobs = []
    new_jobs = [j for j in jobs if j not in old_jobs]
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(old_jobs + new_jobs, f, indent=2)
    return new_jobs

def main():
    all_jobs = []
    print("🔍 Scraping Greenhouse jobs...")
    for slug in GREENHOUSE_SLUGS[25:75]:
        all_jobs.extend(fetch_greenhouse_jobs(slug))
        print(slug)
        time.sleep(0.2)

    print("🔍 Scraping Lever jobs...")
    for slug in LEVER_SLUGS[:1]:
        all_jobs.extend(fetch_lever_jobs(slug))
        time.sleep(0.2)

    filtered = [j for j in all_jobs if is_recent(j['date'])]
    new_jobs = save_jobs(filtered)
    print(f"✅ {len(new_jobs)} new jobs saved.")

if __name__ == "__main__":
    main()
