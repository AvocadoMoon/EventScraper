from src.db_cache import SQLiteDB, UploadedEventRow
from src.mobilizon.mobilizon import MobilizonAPI
from src.mobilizon.mobilizon_types import EventType
from src.website_scraper.google_calendar import GCalAPI
import json
import os
import logging
from src.logger import logger_name, setup_custom_logger

logger = logging.getLogger(logger_name)


class Runner:
    mobilizonAPI: MobilizonAPI
    cache_db: SQLiteDB
    testMode: bool
    fakeUUIDForTests = 0
    google_calendar_api: GCalAPI
    
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
        self.google_calendar_api = GCalAPI()


    def _uploadEventsRetrievedFromCalendarID(self, google_calendar_id, google_calendars, google_calendar_name):
        lastUploadedEventDate = None
        if not self.cache_db.noEntriesWithCalendarID(google_calendar_id):
            lastUploadedEventDate = self.cache_db.getLastEventForCalendarID(google_calendar_id)
        
        events: [EventType] = self.google_calendar_api.getAllEventsAWeekFromNow(
            calendarId=google_calendar_id, calendarDict=google_calendars[google_calendar_name], 
            checkCacheFunction=self.cache_db.entryAlreadyInCache,
            dateOfLastEventScraped=lastUploadedEventDate)
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
            logger.info(f"{uploadResponse}")            
            self.cache_db.insertUploadedEvent(UploadedEventRow(uuid=uploadResponse["uuid"],
                                                id=uploadResponse["id"],
                                                title=event.title,
                                                date=event.beginsOn,
                                                groupID=event.attributedToId,
                                                groupName=google_calendar_name,
                                                calendar_id=google_calendar_id))

    def getGCalEventsAndUploadThem(self):
        google_calendars: dict = None
        with open(f"{os.getcwd()}/src/website_scraper/GCal.json", "r") as f:
            google_calendars = json.load(f)

        for key, value in google_calendars.items():
            logger.info(f"Getting events from calendar {key}")
            for google_calendar_id in google_calendars[key]["googleIDs"]:
                self._uploadEventsRetrievedFromCalendarID(google_calendar_id, google_calendars, key)
    
    def getGCalEventsForSpecificGroupAndUploadThem(self, calendarGroup: str):
        google_calendars: dict = None
        with open(f"{os.getcwd()}/src/website_scraper/GCal.json", "r") as f:
            google_calendars = json.load(f)
        
        logger.info(f"Getting events from calendar {calendarGroup}")
        for google_calendar_id in google_calendars[calendarGroup]["googleIDs"]:
            self._uploadEventsRetrievedFromCalendarID(google_calendar_id, google_calendars, calendarGroup)
             
    
    def cleanUp(self):
        self.mobilizonAPI.logout()
        self.cache_db.close()
        self.google_calendar_api.close()
    

if __name__ == "__main__":
    setup_custom_logger(logging.INFO)
    runner = Runner()
    runner.getGCalEventsAndUploadThem()
    runner.cleanUp()
