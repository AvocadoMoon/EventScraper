import json
import logging
import os
import urllib.request

from src.db_cache import ScraperTypes
from src.logger import logger_name
from src.publishers.abc_publisher import Publisher
from src.publishers.mobilizon.types import MobilizonEvent, EventParameters
from src.publishers.mobilizon.uploader import MobilizonUploader
from src.scrapers.abc_scraper import Scraper, GroupEventsKernel


logger = logging.getLogger(logger_name)


def none_if_not_present(x, dictionary):
    return None if x not in dictionary else dictionary[x]

def get_group_kernels(json_path: str, scraper_type: ScraperTypes) -> [GroupEventsKernel]:
    group_schema: dict = None
    with urllib.request.urlopen(json_path) as f:
        group_schema = json.load(f)
    
    all_group_kernels: [GroupEventsKernel] = []
    for group_name, group_info in group_schema.items():

        mobilizon_metadata = group_info["publisherInfo"]["mobilizon"]

        event_address = None if "defaultLocation" not in group_info else EventParameters.Address(**group_info["defaultLocation"])
        category = None if "defaultCategory" not in mobilizon_metadata else EventParameters.Categories[mobilizon_metadata["defaultCategory"]]
        event_kernel = MobilizonEvent(mobilizon_metadata["groupID"], none_if_not_present("title", group_info),
                                     none_if_not_present("defaultDescription", group_info), none_if_not_present("beginsOn", group_info),
                                     group_info["onlineAddress"], none_if_not_present("endsOn", group_info),
                                     event_address, category,
                                     none_if_not_present("defaultTags", mobilizon_metadata), EventParameters.MediaInput(mobilizon_metadata["defaultImageID"]))

        calendar_ids = group_info["calendarIDs"]

        all_group_kernels.append(
            GroupEventsKernel(event_kernel, group_name, calendar_ids=calendar_ids, scraper_type=scraper_type, json_source_url=json_path))
    
    return all_group_kernels


from src.scrapers.google_calendar.scraper import GoogleCalendarScraper
from src.scrapers.statics.scraper import StaticScraper

def get_scrapers_and_publishers(test_mode, cache_db, submission_path=None) -> {Publisher: [(Scraper, [
    GroupEventsKernel])]}:
    scraper_and_publisher: dict = None
    submission_json_path = os.getenv("RUNNER_SUBMISSION_JSON_PATH") if submission_path is None else submission_path
    with urllib.request.urlopen(submission_json_path) as f:
        scraper_and_publisher = json.load(f)

    submission: {Publisher: [(Scraper, [GroupEventsKernel])]} = dict()
    for publisher in scraper_and_publisher.keys():
        publisher_instance: Publisher
        match publisher:
            case "Mobilizon":
                publisher_instance = MobilizonUploader(test_mode, cache_db)
        submission[publisher_instance] = []
        scrapers:dict = scraper_and_publisher.get(publisher)
        for scraper_type_name in scrapers.keys():
            scraper_class: Scraper.__class__ = None
            scraper_type: ScraperTypes
            match scraper_type_name:
                case "GoogleCalendarKernelSources":
                    scraper_class = GoogleCalendarScraper
                    scraper_type = ScraperTypes.gCal
                case "StaticKernelSources":
                    scraper_class = StaticScraper
                    scraper_type = ScraperTypes.json

            for kernel_source in scrapers[scraper_type_name]:
                group_kernels = get_group_kernels(kernel_source, scraper_type)
                scraper_and_source = (scraper_class(cache_db), group_kernels)
                submission[publisher_instance].append(scraper_and_source)

    return submission










