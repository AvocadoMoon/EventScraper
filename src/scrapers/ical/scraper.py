import copy
import logging
import os
import urllib.request
from datetime import datetime, timedelta, timezone

import icalendar
from geopy import Nominatim
from icalendar.cal import Calendar

from src.db_cache import SQLiteDB, ScraperTypes
from src.logger import logger_name
from src.parser.types import GroupEventsKernel, EventsToUploadFromCalendarID
from src.publishers.mobilizon.api import logger
from src.publishers.mobilizon.types import MobilizonEvent, EventParameters
from src.scrapers.abc_scraper import Scraper, find_geolocation_from_address
from src.scrapers.google_calendar.api import parse_google_location

logger = logging.getLogger(logger_name)


class ICALScraper(Scraper):
    def get_source_type(self):
        return ScraperTypes.GOOGLE_CAL

    cache_db: SQLiteDB
    def __init__(self, cache_db: SQLiteDB):
        super().__init__(cache_db)
        self.cache_db = cache_db

    def retrieve_from_source(self, group_event_kernel: GroupEventsKernel) -> [EventsToUploadFromCalendarID]:
        all_events: [EventsToUploadFromCalendarID] = []
        logger.info(f"Getting events from calendar {group_event_kernel.group_name}")
        for ical_id in group_event_kernel.calendar_ids:
            with urllib.request.urlopen(ical_id) as f:
                calendar = icalendar.Calendar.from_ical(f.read())
                events = _hydrate_event_template(calendar, group_event_kernel.event_template)
                all_events.append(EventsToUploadFromCalendarID(events, group_event_kernel, ical_id))

        return all_events

    # Get only events 1 week from today, and that are confirmed

    def close(self):
        pass
    def connect_to_source(self):
        pass

    def _convert_scrapped_info_to_upload(self):
        pass


def _hydrate_event_template(calendar: Calendar, event_kernel: MobilizonEvent) -> [MobilizonEvent]:
    week_from_now = datetime.now(timezone.utc) + timedelta(days=7)
    events = []
    for event in calendar.walk('VEVENT'):
        event_template = copy.deepcopy(event_kernel)
        start = event.get("DTSTART").dt
        end = event.get("DTEND").dt
        summary = str(event.get("SUMMARY"))
        status = event.get("STATUS")
        if start > week_from_now and os.getenv("TEST") != "True":
            break
        elif start < datetime.now(timezone.utc) and os.getenv("TEST") != "True":
            continue
        elif status == "CONFIRMED":
            event_template.title = summary
            event_template.beginsOn = start.isoformat()
            event_template.endsOn = end.isoformat()
            grabbed_description = "" if "DESCRIPTION" not in event else str(event.get("DESCRIPTION"))
            notif = ""
            event_template.onlineAddress = event_template.onlineAddress if "URL" not in event else str(event.get("URL"))
            if "LOCATION" in event:
                parsed_location = _parse_retrieved_location(str(event.get("LOCATION")), event_template.physicalAddress)
                event_template.physicalAddress, notif = find_geolocation_from_address(parsed_location,
                                                                               event_template.physicalAddress,
                                                                               event_template.title)
            event_template.description = f"Automatically scraped by Event Bot {notif}: \n\n{grabbed_description}"
            events.append(event_template)

    return events


def _parse_retrieved_location(location: str, default_location: EventParameters.Address) -> EventParameters.Address:
    if location is None:
        logger.debug("No location provided, using default")
        return default_location
    tokens = location.split(",")
    address: EventParameters.Address
    match len(tokens):
        case 1:
            return default_location
        case 2:
            return default_location
        case 3:
            address = EventParameters.Address(locality=tokens[2], street=tokens[1])
        case 4:
            address = EventParameters.Address(locality=tokens[2], street=tokens[1],
                                              region=tokens[3])
        case 5:
            address = EventParameters.Address(locality=tokens[2], postalCode=tokens[4], street=tokens[1],
                                            region=tokens[3])
        case _:
            return default_location
    return address


