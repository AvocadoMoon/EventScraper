import logging
import os

from src.db_cache import SourceTypes
from src.jsonParser import GroupEventsKernel, get_event_objects, generate_events_from_static_event_kernels
from src.logger import logger_name
from src.publishers.mobilizon.types import MobilizonEvent
from src.scrapers.abc_scraper import Scraper, EventsToUploadFromSourceID

logger = logging.getLogger(logger_name)

class StaticScraper(Scraper):

    def get_source_type(self):
        return SourceTypes.json

    def _convert_scrapped_info_to_upload(self):
        pass

    def connect_to_source(self):
        pass

    def retrieve_from_source(self, group_kernel: GroupEventsKernel) -> [EventsToUploadFromSourceID]:
        json_path = "https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/farmers_market.json"
        logger.info(f"Getting farmer market events for {group_kernel.group_name}")
        events: [MobilizonEvent] = generate_events_from_static_event_kernels(json_path, group_kernel)
        event: MobilizonEvent
        for event in events:
            event.description = f"Automatically scraped by event bot: \n\n{event.description} \n\n Source for farmer market info: https://portal.ct.gov/doag/adarc/adarc/farmers-market-nutrition-program/authorized-redemption-locations"
        return [EventsToUploadFromSourceID(events, group_kernel, group_kernel.group_name)]

    def close(self):
        pass