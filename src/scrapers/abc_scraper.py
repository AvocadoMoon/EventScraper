
from abc import ABC, abstractmethod


from src.jsonParser import GroupEventsKernel
from src.publishers.mobilizon.types import MobilizonEvent

def _generate_args(localVariables: dict) -> dict:
    args = {}
    for name, value in localVariables.items():
        if (value is not None and name != "self" and name != "__class__"):
            args[name] = value
    return args




class EventsToUploadFromCalendarID:
    events: [MobilizonEvent] = None
    eventKernel: GroupEventsKernel = None
    calendar_id: str = ""

    def __init__(self, events: [MobilizonEvent], event_kernel: GroupEventsKernel, source_id: str):
        self.events = events
        self.eventKernel = event_kernel
        self.calendar_id = source_id


class Scraper(ABC):
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





