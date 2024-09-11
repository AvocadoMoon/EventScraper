from src.db_cache import SQLiteDB, UploadedEventRow, UploadSource, SourceTypes
from src.mobilizon.mobilizon import MobilizonAPI
from src.mobilizon.mobilizon_types import EventType, _generate_args
from src.scrapers.google_calendar.api import GCalAPI, ExpiredToken
import json
import os
import logging
from src.logger import logger_name, setup_custom_logger
from src.jsonParser import getEventObjects, EventKernel, generateEventsFromStaticEventKernels
from requests.exceptions import HTTPError
from slack_sdk.webhook import WebhookClient
from pydantic import BaseModel
import time
import datetime

logger = logging.getLogger(logger_name)


class Runner:
    mobilizonAPI: MobilizonAPI
    cache_db: SQLiteDB
    testMode: bool
    fakeUUIDForTests = 0
    google_calendar_api: GCalAPI
    
    def __init__(self, testMode:bool = False):
        secrets = None
        endpoint = os.environ.get("MOBILIZON_ENDPOINT")
        email = os.environ.get("MOBILIZON_EMAIL")
        passwd = os.environ.get("MOBILIZON_PASSWORD")
        
        if email is None and passwd is None:
            loginFilePath = os.environ.get("MOBILIZON_LOGIN_FILE")
            with open(loginFilePath, "r") as f:
                secrets = json.load(f)
                email = secrets["email"]
                passwd = secrets["password"]
        
        self.mobilizonAPI = MobilizonAPI(endpoint, email, passwd)
        if testMode:
            self.cache_db = SQLiteDB(inMemorySQLite=True)
        else:
            self.cache_db = SQLiteDB()
        self.testMode = testMode
        self.google_calendar_api = GCalAPI()


    def _uploadEvent(self, event: EventType, eventKernel: EventKernel, sourceID):
        event: EventType
        uploadResponse: dict = None
        if not self.cache_db.entryAlreadyInCache(event.beginsOn, event.title, sourceID):
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
                                                            source=sourceID,
                                                            sourceType=eventKernel.sourceType))

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
            self._uploadEvent(event, eventKernel, google_calendar_id)

    def getGCalEventsAndUploadThem(self):
        google_calendars: [EventKernel] = getEventObjects(f"{os.getcwd()}/src/scrapers/google_calendar/GCal.json", SourceTypes.gCal)

        eventKernel: EventKernel
        for eventKernel in google_calendars:
            logger.info(f"Getting events from calendar {eventKernel.eventKernelKey}")
            for google_calendar_id in eventKernel.sourceIDs:
                self._uploadEventsRetrievedFromCalendarID(google_calendar_id, eventKernel)
    
    def getGCalEventsForSpecificGroupAndUploadThem(self, calendarGroup: str):
        google_calendars: [EventKernel] = getEventObjects(f"{os.getcwd()}/src/scrapers/GCal.json")
        logger.info(f"Getting events from calendar {calendarGroup}")
        gCal: EventKernel
        for gCal in google_calendars:
            if gCal.eventKernelKey == calendarGroup:
                for googleCalendarID in gCal.sourceIDs:
                    self._uploadEventsRetrievedFromCalendarID(googleCalendarID, gCal)
    
    def getFarmerMarketsAndUploadThem(self):
        jsonPath = f"{os.getcwd()}/src/scrapers/statics/farmerMarkets.json"
        eventKernels: [EventKernel] = getEventObjects(jsonPath, SourceTypes.json)
        
        eventKernel: EventKernel
        for eventKernel in eventKernels:
            logger.info(f"Getting farmer market events for {eventKernel.eventKernelKey}")
            events: [EventType] = generateEventsFromStaticEventKernels(jsonPath, eventKernel)
            event: EventType
            for event in events:
                event.description = f"Automatically scraped by event bot: \n\n{event.description} \n\n Source for farmer market info: https://portal.ct.gov/doag/adarc/adarc/farmers-market-nutrition-program/authorized-redemption-locations"
                self._uploadEvent(event, eventKernel, eventKernel.sourceIDs[0])
    
    def cleanUp(self):
        self.mobilizonAPI.logout()
        self.cache_db.close()
        self.google_calendar_api.close()


def runner():
    continueScraping = True
    numRetries = 0
    runner = None
    while continueScraping and numRetries < 5:
        try:
            runner = Runner()
            runner.getGCalEventsAndUploadThem()
            runner.getFarmerMarketsAndUploadThem()
            runner.cleanUp()
            continueScraping = False
        except HTTPError as err:
            if err.response.status_code == 500 and err.response.message == 'Too many requests':
                runner.cleanUp()
                numRetries += 1
                logger.warning("Going to sleep then retrying to scrape. Retry Num: " + numRetries)
                time.sleep(120)

def daysToSleep(days):
    now = datetime.datetime.now()
    secondsFromZero = (now.hour * 60 * 60)
    timeAt2AM = 2 * 60 * 60
    timeToSleep = timeAt2AM
    if secondsFromZero > timeAt2AM:
        timeToSleep = ((23 * 60 * 60) - secondsFromZero) + timeAt2AM
    else:
        timeToSleep = timeAt2AM - secondsFromZero
    
    return timeToSleep + (60 * 60 * 24 * days)


def produceSlackMessage(color, title, text, priority):
    return {
            "color": color,
            "author_name": "CTEvent Scraper",
            "author_icon": "https://ctgrassroots.org/favicon.ico",
            "title": title,
            "title_link": "google.com",
            "text": text,
            "fields": [
                {
                    "title": "Priority",
                    "value": priority,
                    "short": "false"
                }
            ],
            "footer": "CTEvent Scraper",
        }


if __name__ == "__main__":
    setup_custom_logger(logging.INFO)
    logger.info("Scraper Started")
    sleeping = 2
    webhook = WebhookClient(os.environ.get("SLACK_WEBHOOK"))
    while True:
        
        timeToSleep = daysToSleep(sleeping)
        logger.info("Scraping")
        try:
            runner()
            logger.info("Sleeping " + str(sleeping) + " Days Until Next Scrape")
        except ExpiredToken:
            logger.warning("Expired token.json needs to be replaced")
            timeToSleep = daysToSleep(1)
            logger.warning("Sleeping only 1 day")
            response = webhook.send(attachments=[
                produceSlackMessage("#e6e209", "Expired Token", "Replace token.json", "Medium")
            ])
        
        except Exception as e:
            logger.error("Unknown Error")
            logger.error(e)
            logger.error("Going to Sleep for 7 days")
            webhook.send(attachments=[
                produceSlackMessage("#ab1a13", "Event Scraper Unknown Error", "Check logs for error.", "High")
            ])
            timeToSleep = daysToSleep(7)
        
        time.sleep(timeToSleep)
    
    logger.info("Scraper Stopped")

