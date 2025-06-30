# push_to_sheets.py
import os
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Constants
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = "Job Tracker"
CREDENTIALS_FILE = "job-sheet-tracker-f24c6fa3179a.json"
RESULTS_FILE = "job_log.json"

# Define the order of columns
HEADER = ["company", "title", "location", "link", "source", "date"]

def get_service():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()

def init_sheet(sheet):
    existing = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A1:F1").execute()
    if not existing.get("values"):
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1:F1",
            valueInputOption="RAW",
            body={"values": [HEADER]}
        ).execute()

def append_jobs(sheet, jobs):
    rows = [[j[col] for col in HEADER] for j in jobs]
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A2",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows}
    ).execute()

def push():
    with open(RESULTS_FILE, "r") as f:
        jobs = json.load(f)

    if not jobs:
        print("No jobs to push.")
        return

    sheet = get_service()
    init_sheet(sheet)
    append_jobs(sheet, jobs)
    print(f"✅ Pushed {len(jobs)} jobs to Google Sheets")

if __name__ == "__main__":
    push()
