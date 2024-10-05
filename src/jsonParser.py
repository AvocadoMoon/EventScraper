import json
import logging
import urllib.request

from src.logger import logger_name
from src.publishers.mobilizon.types import MobilizonEvent, EventParameters
from src.db_cache import ScraperTypes
from datetime import datetime, timedelta
import copy

logger = logging.getLogger(logger_name)



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


def none_if_not_present(x, dictionary):
    return None if x not in dictionary else dictionary[x]

def get_group_kernels(json_path: str, scraper_type: ScraperTypes) -> [GroupEventsKernel]:
    group_schema: dict = None
    with urllib.request.urlopen(json_path) as f:
        group_schema = json.load(f)
    
    all_group_kernels: [GroupEventsKernel] = []
    for group_name, group_info in group_schema.items():

        print(group_info["publisherInfo"])
        mobilizon_metadata = group_info["publisherInfo"]["mobilizon"]

        event_address = None if "defaultLocation" not in group_info else EventParameters.Address(**group_info["defaultLocation"])
        category = None if "defaultCategory" not in mobilizon_metadata else EventParameters.Categories[mobilizon_metadata["defaultCategory"]]
        event_kernel = MobilizonEvent(mobilizon_metadata["groupID"], none_if_not_present("title", group_info),
                                     none_if_not_present("defaultDescription", group_info), none_if_not_present("beginsOn", group_info),
                                     group_info["onlineAddress"], none_if_not_present("endsOn", group_info),
                                     event_address, category,
                                     none_if_not_present("defaultTags", mobilizon_metadata), EventParameters.MediaInput(mobilizon_metadata["defaultImageID"]))

        calendar_ids = group_info["calendarIDs"]

        all_group_kernels.append(GroupEventsKernel(event_kernel, group_name, calendar_ids=calendar_ids, scraper_type=scraper_type, json_source_url=json_path))
    
    return all_group_kernels

    












