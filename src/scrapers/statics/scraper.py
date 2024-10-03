import logging
import os

from src.db_cache import ScraperTypes
from src.jsonParser import GroupEventsKernel, get_group_kernels, generate_events_from_static_group_kernel
from src.logger import logger_name
from src.publishers.mobilizon.types import MobilizonEvent
from src.scrapers.abc_scraper import Scraper, EventsToUploadFromCalendarID

logger = logging.getLogger(logger_name)

class StaticScraper(Scraper):

    def get_source_type(self):
        return ScraperTypes.json

    def _convert_scrapped_info_to_upload(self):
        pass

    def connect_to_source(self):
        pass

    def retrieve_from_source(self, group_kernel: GroupEventsKernel) -> [EventsToUploadFromCalendarID]:
        json_path = "https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/farmers_market.json"
        logger.info(f"Getting farmer market events for {group_kernel.group_name}")
        events: [MobilizonEvent] = generate_events_from_static_group_kernel(json_path, group_kernel)
        event: MobilizonEvent
        for event in events:
            event.description = f"Automatically scraped by event bot: \n\n{event.description} \n\n Source for farmer market info: https://portal.ct.gov/doag/adarc/adarc/farmers-market-nutrition-program/authorized-redemption-locations"
        return [EventsToUploadFromCalendarID(events, group_kernel, group_kernel.group_name)]

    def close(self):
        pass