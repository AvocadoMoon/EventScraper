import logging
from abc import ABC, abstractmethod

from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

from src.db_cache import SQLiteDB
from src.logger import create_logger_from_designated_logger
from src.publishers.mobilizon.types import EventParameters


logger = create_logger_from_designated_logger(__name__)


def _generate_args(localVariables: dict) -> dict:
    args = {}
    for name, value in localVariables.items():
        if (value is not None and name != "self" and name != "__class__"):
            args[name] = value
    return args

def find_geolocation_from_address(address: EventParameters.Address,
                                  default_location: EventParameters.Address,
                                  event_title: str) -> (EventParameters.Address, str):
    # Address given is default, so don't need to call Nominatim
    default_location_notif = "with unverified location for address. Please check address on their website"
    if default_location == address:
        logger.debug(f"{event_title} location included with calendar, but is same as default location.")
        return default_location, default_location_notif
    try:
        geo_locator = Nominatim(user_agent="Mobilizon Event Bot", timeout=10)
        geo_code_location = geo_locator.geocode(f"{address.street}, {address.locality}, {address.postalCode}")
        if geo_code_location is None:
            return default_location, default_location_notif
        address.geom = f"{geo_code_location.longitude};{geo_code_location.latitude}"
        logger.debug(f"{event_title}: Outsourced location was {address.street}, {address.locality}")
        return address, ""
    except GeocoderTimedOut:
        return default_location, default_location_notif


class Scraper(ABC):
    cache_db: SQLiteDB
    def __init__(self, cache_db):
        pass
    @abstractmethod
    def _convert_scrapped_info_to_upload(self):
        pass

    @abstractmethod
    def connect_to_source(self):
        pass

    @abstractmethod
    def retrieve_from_source(self, event_kernel):
        """
        Takes GroupEventKernel and returns [EventsToUploadFromCalendarID]
        """
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_source_type(self):
        pass


