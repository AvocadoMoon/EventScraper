
from abc import ABC, abstractmethod

from src.scrapers.abc_scraper import EventsToUploadFromSourceID


class Publisher(ABC):

    @abstractmethod
    def upload(self, events_to_upload: [EventsToUploadFromSourceID]):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass












