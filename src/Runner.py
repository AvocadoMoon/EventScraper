from src.drivers.mobilizon.db_cache import SQLiteDB, UploadedEventRow
from src.drivers.mobilizon.mobilizon import MobilizonAPI
from src.drivers.mobilizon.mobilizon_types import EventType
from src.website_scraper.google_calendar import GCalAPI
import json
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# TODO: Create tests that simulate the runner and everything it does (except for actually uploading)
# TODO: Ensure the uploaded dates and dates retrieved are the same

class Runner:
    mobilizonAPI: MobilizonAPI
    cache_db: SQLiteDB
    testMode: bool
    fakeUUIDForTests = 0
    
    def __init__(self, testMode:bool = False):
        secrets = None
        endpoint = "https://ctgrassroots.org/graphiql"
        with open(f"{os.getcwd()}/src/secrets.json", "r") as f:
            secrets = json.load(f)
        
        self.mobilizonAPI = MobilizonAPI(endpoint, secrets["email"], secrets["password"])
        if testMode:
            self.cache_db = SQLiteDB(inMemorySQLite=True)
        else:
            self.cache_db = SQLiteDB()
        self.testMode = testMode


    def getGCalEventsAndUploadThem(self):
        def uploadEventsRetrievedFromCalendarID():
            lastUploadedEventDate = None
            if not self.cache_db.noEntriesWithCalendarID(google_calendar_id):
                lastUploadedEventDate = self.cache_db.getLastEventForCalendarID(google_calendar_id)
            
            events: [EventType] = google_calendar_api.getAllEventsAWeekFromNow(
                google_calendar_id, google_calendars[key]["groupID"], 
                google_calendars[key]["defaultImageID"], self.cache_db.entryAlreadyInCache,lastUploadedEventDate)
            if (len(events) == 0):
                return
            for event in events:
                event: EventType
                uploadResponse: dict = None
                if self.testMode:
                    self.fakeUUIDForTests += 1
                    uploadResponse = {"id": 1, "uuid": self.fakeUUIDForTests}
                else:
                    uploadResponse = self.mobilizonAPI.bot_created_event(event)
                print(uploadResponse)
            
                self.cache_db.insertUploadedEvent(UploadedEventRow(uuid=uploadResponse["uuid"],
                                                    id=uploadResponse["id"],
                                                    title=event.title,
                                                    date=event.beginsOn,
                                                    groupID=event.attributedToId,
                                                    groupName=key,
                                                    calendar_id=google_calendar_id))

        google_calendar_api = GCalAPI()
        google_calendars: dict = None
        with open(f"{os.getcwd()}/src/website_scraper/GCal.json", "r") as f:
            google_calendars = json.load(f)

        for key, value in google_calendars.items():
            logger.info(f"Getting events from calendar {key}")
            for google_calendar_id in google_calendars[key]["googleIDs"]:
                uploadEventsRetrievedFromCalendarID()
        
        google_calendar_api.close()
        
    
    def cleanUp(self):
        self.mobilizonAPI.logout()
        self.cache_db.close()
    


