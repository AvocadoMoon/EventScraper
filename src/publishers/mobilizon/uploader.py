import json
import os

from src.db_cache import UploadedEventRow, UploadSource, SQLiteDB
from src.jsonParser import GroupEventsKernel
from src.publishers.abc_publisher import Publisher
from src.publishers.mobilizon.api import MobilizonAPI
from src.publishers.mobilizon.types import MobilizonEvent
import logging
from src.logger import logger_name
from src.scrapers.abc_scraper import EventsToUploadFromCalendarID

logger = logging.getLogger(logger_name)
class MobilizonUploader(Publisher):
    mobilizonAPI: MobilizonAPI
    cache_db: SQLiteDB
    test_mode: bool
    fakeUUIDForTests = 0

    def __init__(self, test_mode, cache_db):
        self.cache_db = cache_db
        self.testMode = test_mode

    def close(self):
        if not self.testMode:
            self.mobilizonAPI.logout()

    def upload(self, sources_list: [EventsToUploadFromCalendarID]):
        for events_to_upload in sources_list:
            all_events = events_to_upload.events
            event_kernel = events_to_upload.eventKernel
            source_id = events_to_upload.calendar_id
            for event in all_events:
                event: MobilizonEvent
                upload_response: dict = {}
                if not self.cache_db.entryAlreadyInCache(event.beginsOn, event.title, source_id):
                    if self.testMode:
                        self.fakeUUIDForTests += 1
                        upload_response = {"id": 1, "uuid": self.fakeUUIDForTests}
                    else:
                        upload_response = self.mobilizonAPI.bot_created_event(event)
                    logger.info(f"{upload_response}")

                    upload_row = UploadedEventRow(uuid=upload_response["uuid"], id=upload_response["id"],
                                                  title=event.title, date=event.beginsOn,
                                                  groupID=event.attributedToId, groupName=event_kernel.group_name)
                    upload_source = UploadSource(uuid=upload_response["uuid"], websiteURL=event.onlineAddress,
                                                 source=source_id, sourceType=event_kernel.scraper_type)
                    self.cache_db.insertUploadedEvent(upload_row, upload_source)

    def connect(self):
        if not self.testMode:
            endpoint = os.environ.get("MOBILIZON_ENDPOINT")
            email = os.environ.get("MOBILIZON_EMAIL")
            passwd = os.environ.get("MOBILIZON_PASSWORD")

            if email is None and passwd is None:
                login_file_path = os.environ.get("MOBILIZON_LOGIN_FILE")
                with open(login_file_path, "r") as f:
                    secrets = json.load(f)
                    email = secrets["email"]
                    passwd = secrets["password"]

            self.mobilizonAPI = MobilizonAPI(endpoint, email, passwd)


