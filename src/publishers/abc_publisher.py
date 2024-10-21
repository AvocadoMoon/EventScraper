
from abc import ABC, abstractmethod


class Publisher(ABC):

    @abstractmethod
    def upload(self, events_to_upload):
        """
        Takes [EventsToUploadFromCalendarID]
        """
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass












