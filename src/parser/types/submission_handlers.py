from src.db_cache import ScraperTypes, SQLiteDB
from src.parser.types.generics import GenericEvent
from src.publishers.abc_publisher import Publisher
from src.scrapers.abc_scraper import Scraper


class TimeInfo:
    """
    Used to hydrate the static event schema,
    """
    default_times: []
    end_time: str

    def __init__(self, default_times, end_time):
        self.default_times = default_times
        self.end_time = end_time

class GroupEventsKernel:
    event_template: GenericEvent
    group_name: str
    calendar_ids: [str]
    scraper_type: ScraperTypes
    json_source_url: str
    default_time_info: TimeInfo

    def __init__(self, event, group_name, calendar_ids, scraper_type, json_source_url,
                 time_info = None):
        self.event_template = event
        self.calendar_ids = calendar_ids
        self.group_name = group_name
        self.scraper_type = scraper_type
        self.json_source_url = json_source_url
        self.default_time_info = time_info

    def __eq__(self, other):
        if not isinstance(other, GroupEventsKernel):
            return False
        compare = self.group_name == other.group_name and self.event_template == other.event_template
        compare = compare and self.calendar_ids == other.calendar_ids and self.scraper_type == other.scraper_type
        compare = compare and self.json_source_url == other.json_source_url
        return compare


class GroupPackage:
    package_name: str
    description: str
    scraper_type_and_kernels: {ScraperTypes: [GroupEventsKernel]}

    def __init__(self, scrapers_with_group_kernels, package_name, description):
        self.scraper_type_and_kernels = scrapers_with_group_kernels
        self.package_name = package_name
        self.description = description


class RunnerSubmission:
    def __init__(self, submitted_db: SQLiteDB,
                 submitted_publishers: {Publisher: [GroupPackage]},
                 test: bool,
                 respective_scrapers: {ScraperTypes: Scraper}):
        self.cache_db = submitted_db
        self.test = test
        self.publishers = submitted_publishers
        self.respective_scrapers = respective_scrapers


class EventsToUploadFromCalendarID:
    events: [GenericEvent] = None
    eventKernel: GroupEventsKernel = None
    calendar_id: str = ""

    def __init__(self, events: [GenericEvent], event_kernel: GroupEventsKernel, source_id: str):
        self.events = events
        self.eventKernel = event_kernel
        self.calendar_id = source_id
