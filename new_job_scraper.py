# job_scraper.py
import json
import requests
import time
from datetime import datetime

GREENHOUSE_FILE = "greenhouse_companies.json"
LEVER_FILE = "lever_companies.json"
RESULTS_FILE = "new_jobs.json"

KEYWORDS = ["software", "engineer", "developer", "fullstack", "quant"]
EXCLUDE = ["senior", "staff", "manager", "lead", "principal"]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def is_relevant_job(title):
    title = title.lower()
    return any(k in title for k in KEYWORDS) and not any(e in title for e in EXCLUDE)


def scrape_greenhouse(slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        jobs = []
        for job in data.get("jobs", []):
            title = job.get("title", "")
            location = job.get("location", {}).get("name", "")
            if is_relevant_job(title) and "united states" in location.lower():
                jobs.append({
                    "source": "greenhouse",
                    "company": slug,
                    "title": title,
                    "location": location,
                    "url": job.get("absolute_url"),
                    "posted_at": datetime.utcnow().isoformat()
                })
        return jobs
    except Exception:
        return []


def scrape_lever(slug):
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        jobs = []
        for job in data:
            title = job.get("text", "")
            location = job.get("categories", {}).get("location", "")
            if is_relevant_job(title) and "united states" in location.lower():
                jobs.append({
                    "source": "lever",
                    "company": slug,
                    "title": title,
                    "location": location,
                    "url": job.get("hostedUrl"),
                    "posted_at": datetime.utcnow().isoformat()
                })
        return jobs
    except Exception:
        return []


def main():
    greenhouse_slugs = load_json(GREENHOUSE_FILE)
    lever_slugs = load_json(LEVER_FILE)

    all_jobs = []
    print("🔍 Scraping Greenhouse jobs...")
    for slug in greenhouse_slugs:
        all_jobs.extend(scrape_greenhouse(slug))
        time.sleep(0.2)  # be polite

    print("🔍 Scraping Lever jobs...")
    for slug in lever_slugs:
        all_jobs.extend(scrape_lever(slug))
        time.sleep(0.2)

    print(f"✅ Found {len(all_jobs)} new jobs")
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_jobs, f, indent=2)


if __name__ == "__main__":
    main()
