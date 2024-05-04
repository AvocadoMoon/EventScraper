from src.drivers.mobilizon.db_cache import SQLiteDB, UploadedEventRow
from src.drivers.mobilizon.mobilizon import MobilizonAPI
from src.drivers.mobilizon.mobilizon_types import EventType
from src.website_scraper.google_calendar import GCalAPI
import json
import os


# TODO: Add column in table for DB cache that says the calendar group it came from
# TODO: Ensure the uploaded dates and dates retrieved are the same
# TODO: Add groupID to google cal JSON

def getGCalEventsAndUploadThem():
    endpoint = "https://ctgrassroots.org/graphiql"
    secrets: dict = None
    with open(f"{os.getcwd()}/src/secrets.json", "r") as f:
        secrets = json.load(f)
    
    google_calendar_api = GCalAPI()
    mobilizonAPI = MobilizonAPI(endpoint, secrets["email"], secrets["password"])
    cache_db = SQLiteDB()
    
    google_calendars: dict = None
    with open(f"{os.getcwd}/src", "r") as f:
        google_calendars = json.load(f)

    for key, value in google_calendars.items():
        print(f"Getting events from {key}")
        for google_calendar_id in google_calendars[key]["googleIDs"]:
            lastUploadedEventDate = cache_db.getLastEventForCalendarID(google_calendar_id)
            events: [EventType] = google_calendar_api.getAllEventsAWeekFromNow(
                google_calendar_id, google_calendars[key]["groupID"], lastUploadedEventDate)
            
            uploadedEvents = []
            for event in events:
                event: EventType
                uploadResponse = mobilizonAPI.bot_created_event(event)
                uploadedEvents.append(UploadedEventRow(uuid=uploadResponse["uuid"],
                                                       id=uploadResponse["id"],
                                                       title=event.title,
                                                       date=event.beginsOn,
                                                       groupID=event.attributedToId,
                                                       groupName=key))
            
            cache_db.insertUploadedEvent(uploadedEvents)
    
    google_calendar_api.close()
    mobilizonAPI.logout()
    cache_db.close()
    


