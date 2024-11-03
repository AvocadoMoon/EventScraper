
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

    @abstractmethod
    def generic_event_converter(self, generic_event):
        pass











