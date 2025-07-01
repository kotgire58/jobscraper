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
CREDENTIALS_FILE = "job-sheet-tracker.json"
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

def get_existing_links(sheet):
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!D2:D").execute()
        links = result.get('values', [])
        return set(link[0] for link in links if link)
    except Exception as e:
        print(f"⚠️ Failed to fetch existing links: {e}")
        return set()

def append_jobs(sheet, jobs):
    # Prepare label row
    now = datetime.now()
    label = f"🆕 New jobs from {now.strftime('%B %d')} - {'Morning' if now.hour < 12 else 'Evening'}"
    separator_row = [[label] + [""] * (len(HEADER) - 1)]

    # Get current number of rows to know where to format
    metadata = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = metadata["sheets"][0]["properties"]["sheetId"]
    existing_values = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:A"
    ).execute()
    num_existing_rows = len(existing_values.get("values", []))

    # Append separator row
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A2",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": separator_row}
    ).execute()

    # Format the separator row red
    sheet.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": num_existing_rows,
                            "endRowIndex": num_existing_rows + 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {"red": 1, "green": 0.8, "blue": 0.8},
                                "textFormat": {"bold": True}
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat)"
                    }
                }
            ]
        }
    ).execute()

    # Append actual job rows
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

    existing_links = get_existing_links(sheet)
    new_jobs = [job for job in jobs if job["link"] not in existing_links]

    if not new_jobs:
        print("No new jobs to add.")
        return

    append_jobs(sheet, new_jobs)
    print(f"✅ Pushed {len(new_jobs)} new jobs to Google Sheets")

if __name__ == "__main__":
    push()
