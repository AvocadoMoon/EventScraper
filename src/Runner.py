from src.db_cache import SQLiteDB, UploadedEventRow, UploadSource, SourceTypes
from src.mobilizon.mobilizon import MobilizonAPI
from src.mobilizon.mobilizon_types import EventType
from src.website_scraper.google_calendar import GCalAPI
import json
import os
import logging
from src.logger import logger_name, setup_custom_logger
from src.jsonParser import getEventObjects, EventKernel

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


    def _uploadEventsRetrievedFromCalendarID(self, google_calendar_id, eventKernel: EventKernel):
        lastUploadedEventDate = None
        if not self.cache_db.noEntriesWithSourceID(google_calendar_id):
            lastUploadedEventDate = self.cache_db.getLastEventDateForSourceID(google_calendar_id)
        
        events: [EventType] = self.google_calendar_api.getAllEventsAWeekFromNow(
            calendarId=google_calendar_id, eventKernel=eventKernel.event, 
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
                                                groupName=eventKernel.eventKernelKey),
                                              UploadSource(uuid=uploadResponse["uuid"],
                                                           websiteURL=event.onlineAddress,
                                                           source=google_calendar_id,
                                                           sourceType=SourceTypes.gCal))

    def getGCalEventsAndUploadThem(self):
        google_calendars: [EventKernel] = getEventObjects(f"{os.getcwd()}/src/website_scraper/GCal.json")

        eventKernel: EventKernel
        for eventKernel in google_calendars:
            logger.info(f"Getting events from calendar {eventKernel.eventKernelKey}")
            for google_calendar_id in eventKernel.sourceIDs:
                self._uploadEventsRetrievedFromCalendarID(google_calendar_id, eventKernel)
    
    def getGCalEventsForSpecificGroupAndUploadThem(self, calendarGroup: str):
        google_calendars: [EventKernel] = getEventObjects(f"{os.getcwd()}/src/website_scraper/GCal.json")
        logger.info(f"Getting events from calendar {calendarGroup}")
        gCal: EventKernel
        for gCal in google_calendars:
            if gCal.eventKernelKey == calendarGroup:
                for googleCalendarID in gCal.sourceIDs:
                    self._uploadEventsRetrievedFromCalendarID(googleCalendarID, gCal)
    
    def getFarmerMarketsAndUploadThem(self):
        pass 
    
    def cleanUp(self):
        self.mobilizonAPI.logout()
        self.cache_db.close()
        self.google_calendar_api.close()
    

if __name__ == "__main__":
    setup_custom_logger(logging.INFO)
    runner = Runner()
    runner.getGCalEventsAndUploadThem()
    runner.cleanUp()
