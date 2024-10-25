
from abc import ABC, abstractmethod

from src.db_cache import SQLiteDB


def _generate_args(localVariables: dict) -> dict:
    args = {}
    for name, value in localVariables.items():
        if (value is not None and name != "self" and name != "__class__"):
            args[name] = value
    return args


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


