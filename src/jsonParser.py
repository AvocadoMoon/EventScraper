import json
import logging
from src.logger import logger_name, setup_custom_logger
from src.mobilizon.mobilizon_types import EventType, EventParameters

logger = logging.getLogger(logger_name)



class EventKernel:
    event: EventType
    eventKey: str
    sourceIDs: [str] = None
    
    def __init__(self, event, eventKey, googleIDs=None):
        self.event = event
        self.googleIDs = googleIDs
        self.eventKernelKey = eventKey




def getEventObjects(jsonPath: str) -> [EventKernel]:
    eventSchema: dict = None
    with open(jsonPath, "r") as f:
        eventSchema = json.load(f)
    
    eventKernels: [EventKernel] = []
    for key, event in eventSchema.items():
        def noneIfNotPresent(x):
            return None if x not in eventSchema else event[x]
        
        
        eventAddress = None if "defaultLocation" not in eventSchema else EventParameters.Address(**event["defaultLocation"])
        eventKernel = EventType(event["groupID"], noneIfNotPresent("title"), 
                            noneIfNotPresent("defaultDescription"), noneIfNotPresent("beginsOn"),
                            event["onlineAddress"], noneIfNotPresent("endsOn"), 
                            eventAddress, event["defaultCategory"], 
                            noneIfNotPresent("defaultTags"), event["defaultImageID"])
    
        googleIDs = noneIfNotPresent("googleIDs")
        eventKernels.append(EventKernel(eventKernel, key, googleIDs))
    
    return eventKernels
    












