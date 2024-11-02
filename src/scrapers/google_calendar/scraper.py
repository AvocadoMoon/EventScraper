import logging
import os

from src.db_cache import SQLiteDB, ScraperTypes
from src.logger import create_logger_from_designated_logger
from src.parser.jsonParser import get_group_package
from src.publishers.mobilizon.api import logger
from src.publishers.mobilizon.types import MobilizonEvent
from src.scrapers.abc_scraper import Scraper
from src.parser.types import GroupEventsKernel, EventsToUploadFromCalendarID
from src.scrapers.google_calendar.api import GCalAPI


logger = create_logger_from_designated_logger(__name__)

class GoogleCalendarScraper(Scraper):
    def get_source_type(self):
        return ScraperTypes.GOOGLE_CAL

    google_calendar_api: GCalAPI
    cache_db: SQLiteDB
    def __init__(self, cache_db: SQLiteDB):
        super().__init__(cache_db)
        self.cache_db = cache_db
        self.google_calendar_api = GCalAPI()

    def _get_specific_calendar_events(self, google_calendar_id, group_kernel: GroupEventsKernel):
        last_uploaded_event_date = None
        if not self.cache_db.no_entries_with_source_id(google_calendar_id):
            last_uploaded_event_date = self.cache_db.get_last_event_date_for_source_id(google_calendar_id)

        events: [MobilizonEvent] = self.google_calendar_api.getAllEventsAWeekFromNow(
            calendarId=google_calendar_id, eventKernel=group_kernel.event_template,
            checkCacheFunction=self.cache_db.entry_already_in_cache,
            dateOfLastEventScraped=last_uploaded_event_date)

        return events


    def retrieve_from_source(self, group_event_kernel: GroupEventsKernel) -> [EventsToUploadFromCalendarID]:


        all_events: [EventsToUploadFromCalendarID] = []
        logger.info(f"Getting events from calendar {group_event_kernel.group_name}")
        for google_calendar_id in group_event_kernel.calendar_ids:
            events = self._get_specific_calendar_events(google_calendar_id, group_event_kernel)
            all_events.append(EventsToUploadFromCalendarID(events, group_event_kernel, google_calendar_id))

        return all_events


    ############################
    # Used Mostly for Testing ##
    ############################
    def get_gcal_events_for_specific_group_and_upload_them(self, calendar_group: str):
        google_calendars: [GroupEventsKernel] = get_group_package(f"{os.getcwd()}/src/scrapers/GCal.json")
        logger.info(f"\nGetting events from calendar {calendar_group}")
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
            token_path = f"{os.getcwd()}/config/token.json" if "GOOGLE_API_TOKEN_PATH" not in os.environ else os.environ.get("GOOGLE_API_TOKEN_PATH")
            self.google_calendar_api.init_calendar_read_client_browser(token_path)
        else:
            self.google_calendar_api.init_calendar_read_client_adc()

    def _convert_scrapped_info_to_upload(self):
        pass