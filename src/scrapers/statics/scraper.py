import copy
from datetime import datetime, timedelta

from src.db_cache import ScraperTypes
from src.logger import create_logger_from_designated_logger
from src.parser.types import GroupEventsKernel, EventsToUploadFromCalendarID
from src.publishers.mobilizon.types import MobilizonEvent
from src.scrapers.abc_scraper import Scraper

logger = create_logger_from_designated_logger(__name__)


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
        events: [MobilizonEvent] = hydrate_event_template_with_legitimate_times(group_kernel)
        event: MobilizonEvent
        for event in events:
            event.description = f"Automatically scraped by event bot: \n\n{event.description} \n\n Source for farmer market info: https://portal.ct.gov/doag/adarc/adarc/farmers-market-nutrition-program/authorized-redemption-locations"
        return [EventsToUploadFromCalendarID(events, group_kernel, group_kernel.group_name)]

    def close(self):
        pass



def hydrate_event_template_with_legitimate_times(group_kernel: GroupEventsKernel) -> [MobilizonEvent]:
    """
    Updating the initial default times from the static event to their relevant times for the week, unless
    the end date has been reached.
    """

    #############################################################
    # There can multiple days in a week when an event can occur #
    #############################################################
    times = group_kernel.default_time_info.default_times

    generated_events = []

    end_date = datetime.fromisoformat(group_kernel.default_time_info.end_time)
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
