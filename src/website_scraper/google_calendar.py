from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from src.mobilizon.mobilizon_types import EventType, EventParameters
import os
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from src.logger import logger_name


logger = logging.getLogger(logger_name)

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


class GCalAPI:
    _apiClient: Resource
    
    def __init__(self):
        self._initCalendarReadClient()
    
    def _initCalendarReadClient(self):
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
            
        
        self._apiClient = build("calendar", "v3", credentials=credentialTokens)
    

    def getAllEventsAWeekFromNow(self, eventKernel: EventType, calendarId: str, 
                                 checkCacheFunction, 
                                 dateOfLastEventScraped: datetime = None) -> [EventType]:
        """Get events all events for that specific calender a week from today.

        Args:
            service (Resource): Calender resource available from creating a client with 'read calender' scope
            calendarId (str): UUID of calender. Same ID used to subscribe to a calender
            dateOfLastEventScraped (str, optional): UTC date with timedelta following isoformat. Have to add 'Z' to isoformat to indicate its UTC time. Defaults to None.
        """
        try:
            # Call the Calendar API, 'Z' indicates UTC time
            stringDateLastEvent = datetime.utcnow().astimezone().isoformat()
            if dateOfLastEventScraped is not None: 
                stringDateLastEvent = dateOfLastEventScraped.isoformat()
            logger.debug(f"Time of last event: {stringDateLastEvent}")
            weekFromNow = datetime.utcnow().astimezone() + timedelta(days=7)
            weekFromNow = weekFromNow.isoformat()
            
            events_result = (
                self._apiClient.events()
                .list(
                    calendarId=calendarId,
                    timeMin=stringDateLastEvent,
                    timeMax=weekFromNow,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            googleEvents = events_result.get("items", [])
            if len(googleEvents) == 0:
                logger.info(f"No upcoming events for calendarID {calendarId}\n")
                return googleEvents

            events = []
            for googleEvent in googleEvents:
                _process_google_event(googleEvent=googleEvent, eventsToUpload=events,
                                    checkCacheForEvent=checkCacheFunction,calendarId=calendarId,
                                    eventKernel=eventKernel)
            
            return events
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
    
    def close(self):
        self._apiClient.close()





def _process_google_event(googleEvent: dict, eventsToUpload: [], checkCacheForEvent, 
                          calendarId: str, eventKernel):
    eventAddress = _parse_google_location(googleEvent.get("location"),
                                          eventKernel.physicalAddress)
    starTimeGoogleEvent = googleEvent["start"].get("dateTime")
    endTimeGooglEvent = googleEvent["end"].get("dateTime")
    title = googleEvent.get("summary")
    description = googleEvent.get("description")

    
    if None not in [starTimeGoogleEvent, endTimeGooglEvent, title, description]:
        startDateTime = datetime.fromisoformat(starTimeGoogleEvent.replace('Z', '+00:00')).astimezone()
        endDateTime = datetime.fromisoformat(endTimeGooglEvent.replace('Z', '+00:00')).astimezone()
        if not checkCacheForEvent(startDateTime.isoformat(), title, calendarId):
            eventKernel.beginsOn = startDateTime.isoformat()
            eventKernel.endsOn = endDateTime.isoformat()
            eventKernel.physicalAddress = eventAddress
            eventKernel.title = title
            eventKernel = f"Automatically scraped by Event Bot: \n\n{description}"
            eventsToUpload.append(eventKernel)
            

def _parse_google_location(location:str, defaultLocation: EventParameters.Address):
    if location is None and defaultLocation is not None:
        logger.debug("No location provided, using default")
        return defaultLocation
    if location is None:
        return None
    tokens = location.split(",")
    address: EventParameters.Address = None
    match len(tokens):
        case 1:
            return defaultLocation
        case 2:
            return defaultLocation
        case 3:
            address = EventParameters.Address(locality=tokens[0], postalCode=tokens[1], street="", country=tokens[2])
        case 4:
            address = EventParameters.Address(locality=tokens[1], postalCode=tokens[2], street=tokens[0], country=tokens[3])
        case 5:
            address = EventParameters.Address(locality=tokens[2], postalCode=tokens[3], street=tokens[1], country=tokens[4])
        case _:
            return None

    # Address given is default, so don't need to call Nominatim
    if (defaultLocation is not None and defaultLocation.locality in location 
        and defaultLocation.street in location and defaultLocation.postalCode in location):
        logger.debug("Location included with calendar, but is same as default location.")
        return defaultLocation
    
    try:
        geo_locator = Nominatim(user_agent="Mobilizon Event Bot", timeout=10)
        geo_code_location = geo_locator.geocode(f"{address.street}, {address.locality}, {address.postalCode}")
        if geo_code_location is None:
            return None
        address.geom = f"{geo_code_location.longitude};{geo_code_location.latitude}"
        logger.info(f"Outsourced location info. Outsourced location was {address.street}, {address.locality}")
        return address
    except GeocoderTimedOut:
        return None