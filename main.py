import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scopes for accessing Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events.owned']

        

def main():
    """Authenticate with Google Calendar API."""
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)

            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def list_events():
    """List the next 10 events from the user's Google Calendar."""
    creds = main()
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow()
    end_time = now + datetime.timedelta(days=7)  # Adjust as needed

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        print(start_time, event["summary"])

    try:
        event = {
            "summary": "Veevart Quiz",
            "Location": "Online",
            "description": "Quiz about Google Calendar",
            "colorId": 3,
            "start": {
                "dateTime": "2023-12-26T14:00:00+02:00",
                "timeZone": "America/Bogota"
            },
            "end": {
                "dateTime": "2023-12-26T18:00:00+02:00",
                "timeZone": "America/Bogota"
            },
            "recurrence": [
                "RRULE :FREQ=DAILY;COUNT=1"
            ],
            "attendees": [
                {"email": "manuel@veevart.com"},
                {"email": "camilo_aea@hotmai.com"}
            ]
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event successfully created { event.get('htmlLink')}")
    
    except HttpError as error:
        print(f"An error occurred: {error}")
    
if __name__ == '__main__':
    list_events()

