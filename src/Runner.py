from src.drivers.mobilizon.db_cache import SQLiteDB, UploadedEventRow
from src.drivers.mobilizon.mobilizon import MobilizonAPI
from src.drivers.mobilizon.mobilizon_types import EventType
from src.website_scraper.google_calendar import GCalAPI
import json
import os

# TODO: Create tests that simulate the runner and everything it does (except for actually uploading)
# TODO: Ensure the uploaded dates and dates retrieved are the same

class Runner:
    mobilizonAPI: MobilizonAPI
    cache_db: SQLiteDB
    testMode: bool
    
    def __init__(self, testMode:bool = False):
        secrets = None
        endpoint = "https://ctgrassroots.org/graphiql"
        with open(f"{os.getcwd()}/src/secrets.json", "r") as f:
            self.secrets = json.load(f)
        
        self.mobilizonAPI = MobilizonAPI(endpoint, secrets["email"], secrets["password"])
        if testMode:
            self.cache_db = SQLiteDB(inMemorySQLite=True)
        else:
            self.cache_db = SQLiteDB()
        self.testMode = testMode


    def getGCalEventsAndUploadThem(self):
        google_calendar_api = GCalAPI()
        
        google_calendars: dict = None
        with open(f"{os.getcwd}/src", "r") as f:
            google_calendars = json.load(f)

        for key, value in google_calendars.items():
            print(f"Getting events from {key}")
            for google_calendar_id in google_calendars[key]["googleIDs"]:
                lastUploadedEventDate = self.cache_db.getLastEventForCalendarID(google_calendar_id)
                events: [EventType] = google_calendar_api.getAllEventsAWeekFromNow(
                    google_calendar_id, google_calendars[key]["groupID"], 
                    google_calendars[key]["defaultImageID"] ,lastUploadedEventDate)
                
                uploadedEvents = []
                for event in events:
                    event: EventType
                    uploadedEvents: dict
                    fakeUUIDForTests = 0
                    if not self.testMode:
                        uploadResponse = self.mobilizonAPI.bot_created_event(event)
                    else:
                        fakeUUIDForTests += 1
                        uploadResponse = {"id": 1, "uuid": fakeUUIDForTests}
                    uploadedEvents.append(UploadedEventRow(uuid=uploadResponse["uuid"],
                                                        id=uploadResponse["id"],
                                                        title=event.title,
                                                        date=event.beginsOn,
                                                        groupID=event.attributedToId,
                                                        groupName=key))
                
                self.cache_db.insertUploadedEvent(uploadedEvents)
        
        google_calendar_api.close()
        
    
    def cleanUp(self):
        self.mobilizonAPI.logout()
        self.cache_db.close()
    


