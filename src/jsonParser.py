import json
import logging
from src.logger import logger_name, setup_custom_logger
from src.mobilizon.mobilizon_types import EventType, EventParameters

logger = logging.getLogger(logger_name)



class EventKernel:
    event: EventType
    eventKey: str
    sourceIDs: [str]
    
    def __init__(self, event, eventKey, sourceIDs):
        self.event = event
        self.sourceIDs = sourceIDs
        self.eventKernelKey = eventKey




def getEventObjects(jsonPath: str) -> [EventKernel]:
    eventSchema: dict = None
    with open(jsonPath, "r") as f:
        eventSchema = json.load(f)
    
    eventKernels: [EventKernel] = []
    for key, event in eventSchema.items():
        def noneIfNotPresent(x):
            return None if x not in event else event[x]
        
        
        eventAddress = None if "defaultLocation" not in eventSchema else EventParameters.Address(**event["defaultLocation"])
        category = None if "defaultCategory" not in eventSchema else EventParameters.Categories[event["defaultCategory"]]
        eventKernel = EventType(event["groupID"], noneIfNotPresent("title"), 
                            noneIfNotPresent("defaultDescription"), noneIfNotPresent("beginsOn"),
                            event["onlineAddress"], noneIfNotPresent("endsOn"), 
                            eventAddress, category, 
                            noneIfNotPresent("defaultTags"), EventParameters.MediaInput(event["defaultImageID"]))

        googleIDs = noneIfNotPresent("googleIDs")
        eventKernels.append(EventKernel(eventKernel, key, sourceIDs=googleIDs))
    
    return eventKernels
    












