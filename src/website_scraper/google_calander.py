from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import os

# Subscribe to the calendars
# https://webapps.stackexchange.com/questions/5217/how-can-i-find-the-subscribe-url-from-the-google-calendar-embed-source-code

# Bike Shop Source 
# bsbc.co_c4dt5esnmutedv7p3nu01aerhk@group.calendar.google.com

# Save The Sound Source
# ctenvironment@gmail.com

# Google API Documentation
# https://console.cloud.google.com/apis/credentials/consent
# https://developers.google.com/calendar/api/quickstart/python
def main():
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    credentialTokens = None
    credential_token_path = f"{os.getcwd()}/src/token.json"
    if os.path.exists(credential_token_path):
        credentialTokens = Credentials.from_authorized_user_file(credential_token_path, SCOPES)
    
    if not credentialTokens or not credentialTokens.valid:
        if credentialTokens and credentialTokens.expired and credentialTokens.refresh_token:
            credentialTokens.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    f"{os.getcwd()}/src/OAuthClientApp.json", SCOPES
                )
            credentialTokens = flow.run_local_server(port=9000)
        
        # When refreshed authentication token needs to be re-written, and if authenticating for the first time it needs to be just written
        with open(credential_token_path, "w") as tokenFile:
            tokenFile.write(credentialTokens.to_json())
        
    try:
        service = build("calendar", "v3", credentials=credentialTokens)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="bsbc.co_c4dt5esnmutedv7p3nu01aerhk@group.calendar.google.com",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")

main()