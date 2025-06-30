# send_summary.py
import json
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

LOG_FILE = "job_log.json"
TODAY = datetime.now().date().isoformat()

EMAIL = os.getenv("GMAIL_USER")
APP_PASS = os.getenv("GMAIL_APP_PASSWORD")
TO_EMAIL = EMAIL  # send to self
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


def load_today_jobs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        jobs = json.load(f)
    return [j for j in jobs if j["date"].startswith(TODAY)]


def send_email(jobs):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = f"🧠 {len(jobs)} New Jobs Found Today"

    content = "\n\n".join(f"{j['title']} at {j['company']}\n{j['link']}" for j in jobs)
    msg.attach(MIMEText(content, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASS)
        server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
    print("📧 Email sent.")


def send_discord(jobs):
    if not DISCORD_WEBHOOK:
        print("No Discord webhook set.")
        return

    content = f"**🧠 {len(jobs)} New Jobs Posted Today:**\n"
    for job in jobs:
        content += f"\n[`{job['company']}`] {job['title']} → {job['link']}"

    payload = {"content": content[:2000]}  # Discord limit
    requests.post(DISCORD_WEBHOOK, json=payload)
    print("🔔 Discord notification sent.")


def main():
    jobs = load_today_jobs()
    if not jobs:
        print("No new jobs today.")
        return
    send_email(jobs)
    send_discord(jobs)


if __name__ == "__main__":
    main()