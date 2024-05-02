from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from src.drivers.mobilizon.mobilizon_types import EventType, EventParameters
import os

# Subscribe to the calendars
# https://webapps.stackexchange.com/questions/5217/how-can-i-find-the-subscribe-url-from-the-google-calendar-embed-source-code
# http://www.google.com/calendar/feeds/HERE/public/basic

# Bike Shop Source 
# bsbc.co_c4dt5esnmutedv7p3nu01aerhk@group.calendar.google.com

# Save The Sound Source
# ctenvironment@gmail.com

# Google API Documentation
# https://console.cloud.google.com/apis/credentials/consent
# https://developers.google.com/calendar/api/quickstart/python
# https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/calendar_v3.events.html#list


def getCalenderReadClient():
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
        
    
    return build("calendar", "v3", credentials=credentialTokens)

def getAllEventsAWeekFromNow(service: Resource, calendarId: str, dateOfLastEventScraped: str = None) -> [EventType]:
    """Get events all events for that specific calender a week from today.

    Args:
        service (Resource): Calender resource available from creating a client with 'read calender' scope
        calendarId (str): UUID of calender. Same ID used to subscribe to a calender
        dateOfLastEventScraped (str, optional): UTC date with timedelta following isoformat. Have to add 'Z' to isoformat to indicate its UTC time. Defaults to None.
    """
    try:
        # Call the Calendar API, 'Z' indicates UTC time
        dateOfLastEventScraped = datetime.utcnow().isoformat() + "Z" if dateOfLastEventScraped is None else dateOfLastEventScraped
        weekFromNow = datetime.utcnow() + timedelta(days=7)
        weekFromNow = weekFromNow.isoformat() + "Z"
        
        events_result = (
            service.events()
            .list(
                calendarId=calendarId,
                timeMin=dateOfLastEventScraped,
                timeMax=weekFromNow,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        googleEvents = events_result.get("items", [])
        if not googleEvents:
            print("No upcoming events found.")
            return

        events = []
        for googleEvent in googleEvents:
            eventAddress = _parse_google_location(googleEvent.get("location"))
            event = EventType(attributedToId=0, 
                              title= googleEvent["summary"], description=googleEvent.get("description"),
                              beginsOn=googleEvent["start"].get("dateTime"),
                              endsOn=googleEvent["end"].get("dateTime"),
                              onlineAddress="", physicalAddress=eventAddress,
                              category=None, tags=None)
            events.append(event)
        
        return events
    except HttpError as error:
        print(f"An error occurred: {error}")

def _parse_google_location(location:str):
    return None if location is None else None
    tokens = location.split(",")
    address: EventParameters.Address = None
    match len(tokens):
        case 3:
            address = EventParameters.Address(locality=tokens[0], postalCode=tokens[1], street="", country=tokens[2])
        case 4:
            address = EventParameters.Address(locality=tokens[1], postalCode=tokens[2], street=tokens[0], country=tokens[3])
        case 5:
            address = EventParameters.Address(locality=tokens[2], postalCode=tokens[3], street=tokens[1], country=tokens[4])

    return address