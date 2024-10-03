import logging
import os

from src.db_cache import SQLiteDB, ScraperTypes
from src.jsonParser import GroupEventsKernel, get_group_kernels
from src.logger import logger_name
from src.publishers.mobilizon.api import logger
from src.publishers.mobilizon.types import MobilizonEvent
from src.scrapers.abc_scraper import Scraper, EventsToUploadFromCalendarID
from src.scrapers.google_calendar.api import GCalAPI


logger = logging.getLogger(logger_name)

class GoogleCalendarScraper(Scraper):
    def get_source_type(self):
        return ScraperTypes.gCal

    google_calendar_api: GCalAPI
    cache_db: SQLiteDB
    def __init__(self, cache_db: SQLiteDB):
        self.google_calendar_api = GCalAPI()
        self.cache_db = cache_db

    def _get_specific_calendar_events(self, google_calendar_id, group_kernel: GroupEventsKernel):
        last_uploaded_event_date = None
        if not self.cache_db.noEntriesWithSourceID(google_calendar_id):
            last_uploaded_event_date = self.cache_db.getLastEventDateForSourceID(google_calendar_id)

        events: [MobilizonEvent] = self.google_calendar_api.getAllEventsAWeekFromNow(
            calendarId=google_calendar_id, eventKernel=group_kernel.event_template,
            checkCacheFunction=self.cache_db.entryAlreadyInCache,
            dateOfLastEventScraped=last_uploaded_event_date)

        return events


    def retrieve_from_source(self, group_event_kernel: GroupEventsKernel) -> [EventsToUploadFromCalendarID]:


        all_events: [EventsToUploadFromCalendarID] = []
        logger.info(f"Getting events from calendar {group_event_kernel.group_name}")
        for google_calendar_id in group_event_kernel.calendar_ids:
            events = self._get_specific_calendar_events(google_calendar_id, group_event_kernel)
            all_events += EventsToUploadFromCalendarID(events, group_event_kernel, google_calendar_id)

        return all_events


    ############################
    # Used Mostly for Testing ##
    ############################
    def get_gcal_events_for_specific_group_and_upload_them(self, calendar_group: str):
        google_calendars: [GroupEventsKernel] = get_group_kernels(f"{os.getcwd()}/src/scrapers/GCal.json")
        logger.info(f"Getting events from calendar {calendar_group}")
        gCal: GroupEventsKernel
        all_events: [MobilizonEvent] = []
        for gCal in google_calendars:
            if gCal.group_name == calendar_group:
                for googleCalendarID in gCal.calendar_ids:
                    all_events += self._get_specific_calendar_events(googleCalendarID, gCal)
        return all_events

    def close(self):
        self.google_calendar_api.close()

    def connect_to_source(self):
        use_oidc = os.environ.get("USE_OIDC_TOKEN")
        if use_oidc:
            self.google_calendar_api.init_calendar_read_client_browser()
        else:
            self.google_calendar_api.init_calendar_read_client_adc()

    def _convert_scrapped_info_to_upload(self):
        pass