# send_notifications.py
import os
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

JOB_FILE = "newly_pushed_jobs.json"


def load_jobs():
    if not os.path.exists(JOB_FILE):
        return []
    with open(JOB_FILE, 'r') as f:
        return json.load(f)

def summarize_jobs(jobs):
    lines = []
    for job in jobs:  # last 10 jobs
        line = f"**{job['title']}** at *{job['company']}*\n<{job['link']}>\nLocation: {job['location']}\n"
        lines.append(line)
    return "\n---\n".join(lines)

def send_discord_message(message):
    if not DISCORD_WEBHOOK:
        return
    payload = {
        "content": f"🚨 **Daily Job Digest** — {len(jobs)} new jobs today!\n\n{message}"
    }
    requests.post(DISCORD_WEBHOOK, json=payload)

def send_email(message):
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
        return
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"🛠️ {len(jobs)} New Jobs Found Today!"
    msg.attach(MIMEText(message, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def notify():
    global jobs
    jobs = load_jobs()
    if not jobs:
        print("No jobs to notify.")
        return
    message = summarize_jobs(jobs)
    send_discord_message(message)
    send_email(message)
    print("✅ Notifications sent!")

if __name__ == "__main__":
    notify()
