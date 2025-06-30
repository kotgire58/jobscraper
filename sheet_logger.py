# sheet_logger.py
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_NAME = os.getenv("SHEET_NAME", "Hidden Jobs Tracker")
LOG_FILE = "job_log.json"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("job-sheet-tracker.json", scope)
client = gspread.authorize(creds)

try:
    sheet = client.open(SHEET_NAME).sheet1
except:
    sheet = client.create(SHEET_NAME).sheet1
    sheet.append_row(["Date", "Company", "Title", "Link"])

def already_logged(link):
    records = sheet.col_values(4)
    return link in records

def main():
    with open(LOG_FILE, "r") as f:
        jobs = json.load(f)

    count = 0
    for job in jobs:
        if not already_logged(job['link']):
            sheet.append_row([
                job['date'],
                job['company'],
                job['title'],
                job['link']
            ])
            count += 1

    print(f"📝 {count} new jobs written to sheet.")

if __name__ == "__main__":
    main()
