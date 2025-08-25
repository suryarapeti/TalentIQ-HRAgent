import os
import pickle
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        with open("token.json", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8081)
        with open("token.json", "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)

def schedule_interview(candidate_name, start_time, duration_minutes=30):
        service = get_calendar_service()
        event = {
            "summary": f"Interview with {candidate_name}",
            "description": f"Interview scheduled with candidate {candidate_name}.",
            "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
            "end": {
                "dateTime": (pd.to_datetime(start_time) + pd.Timedelta(minutes=duration_minutes)).isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "attendees": [],
        }
        event = service.events().insert(calendarId="primary", body=event).execute()
        return event.get("htmlLink")
