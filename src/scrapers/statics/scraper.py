import copy
import json
import logging
import os
import urllib
import urllib.request
from datetime import datetime, timedelta

from src.db_cache import ScraperTypes
from src.jsonParser import get_group_kernels
from src.logger import logger_name
from src.publishers.mobilizon.types import MobilizonEvent
from src.scrapers.abc_scraper import Scraper, EventsToUploadFromCalendarID, GroupEventsKernel

logger = logging.getLogger(logger_name)

class StaticScraper(Scraper):

    def get_source_type(self):
        return ScraperTypes.STATIC

    def _convert_scrapped_info_to_upload(self):
        pass

    def connect_to_source(self):
        pass

    def retrieve_from_source(self, group_kernel: GroupEventsKernel) -> [EventsToUploadFromCalendarID]:
        json_path = group_kernel.json_source_url
        logger.info(f"\nGetting farmer market events for {group_kernel.group_name}")
        events: [MobilizonEvent] = hydrate_event_template_with_legitimate_times(json_path, group_kernel)
        event: MobilizonEvent
        for event in events:
            event.description = f"Automatically scraped by event bot: \n\n{event.description} \n\n Source for farmer market info: https://portal.ct.gov/doag/adarc/adarc/farmers-market-nutrition-program/authorized-redemption-locations"
        return [EventsToUploadFromCalendarID(events, group_kernel, group_kernel.group_name)]

    def close(self):
        pass


def hydrate_event_template_with_legitimate_times(json_path: str, group_kernel: GroupEventsKernel) -> [MobilizonEvent]:
    event_schema: dict = None
    with urllib.request.urlopen(json_path) as f:
        event_schema = json.load(f)

    #############################################################
    # There can multiple days in a week when an event can occur #
    #############################################################
    times = event_schema[group_kernel.group_name]["defaultTimes"]

    generated_events = []

    end_date = datetime.fromisoformat(event_schema[group_kernel.group_name]["endDate"])
    now = datetime.utcnow().astimezone()

    if now.date() <= end_date.date():
        for t in times:
            event: MobilizonEvent = copy.deepcopy(group_kernel.event_template)
            start_time = datetime.fromisoformat(t[0])
            end_time = datetime.fromisoformat(t[1])

            time_difference_weeks = (now - start_time).days // 7  # Floor division that can result in week prior event

            start_time += timedelta(weeks=time_difference_weeks)
            end_time += timedelta(weeks=time_difference_weeks)

            if start_time < now:
                start_time += timedelta(weeks=1)
                end_time += timedelta(weeks=1)
                if start_time > end_date:
                    return []

            event.beginsOn = start_time.astimezone().isoformat()
            event.endsOn = end_time.astimezone().isoformat()

            generated_events.append(event)

        return generated_events

    logger.info(f"Static Event {group_kernel.group_name} Has Expired")
    return []
