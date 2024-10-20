
from abc import ABC, abstractmethod

from src.db_cache import ScraperTypes, SQLiteDB
from src.publishers.mobilizon.types import MobilizonEvent

def _generate_args(localVariables: dict) -> dict:
    args = {}
    for name, value in localVariables.items():
        if (value is not None and name != "self" and name != "__class__"):
            args[name] = value
    return args


class GroupEventsKernel:
    event_template: MobilizonEvent
    group_name: str
    calendar_ids: [str]
    scraper_type: ScraperTypes
    json_source_url: str

    def __init__(self, event, group_name, calendar_ids, scraper_type, json_source_url):
        self.event_template = event
        self.calendar_ids = calendar_ids
        self.group_name = group_name
        self.scraper_type = scraper_type
        self.json_source_url = json_source_url

    def __eq__(self, other):
        if not isinstance(other, GroupEventsKernel):
            return False
        compare = self.group_name == other.group_name and self.event_template == other.event_template
        compare = compare and self.calendar_ids == other.calendar_ids and self.scraper_type == other.scraper_type
        compare = compare and self.json_source_url == other.json_source_url
        return compare

class EventsToUploadFromCalendarID:
    events: [MobilizonEvent] = None
    eventKernel: GroupEventsKernel = None
    calendar_id: str = ""

    def __init__(self, events: [MobilizonEvent], event_kernel: GroupEventsKernel, source_id: str):
        self.events = events
        self.eventKernel = event_kernel
        self.calendar_id = source_id


class Scraper(ABC):
    cache_db: SQLiteDB
    def __init__(self, cache_db):
        self.cached_db = cache_db

    @abstractmethod
    def _convert_scrapped_info_to_upload(self):
        pass

    @abstractmethod
    def connect_to_source(self):
        pass

    @abstractmethod
    def retrieve_from_source(self, event_kernel: GroupEventsKernel) -> [EventsToUploadFromCalendarID]:
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_source_type(self):
        pass



