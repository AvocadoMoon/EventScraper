import json
import logging
from src.logger import logger_name
from src.publishers.mobilizon import EventType, EventParameters
from src.db_cache import SourceTypes
from datetime import datetime, timedelta
import copy

logger = logging.getLogger(logger_name)



class EventKernel:
    event: EventType
    eventKernelKey: str
    sourceIDs: [str]
    sourceType: SourceTypes
    
    def __init__(self, event, eventKey, sourceIDs, sourceType):
        self.event = event
        self.sourceIDs = sourceIDs
        self.eventKernelKey = eventKey
        self.sourceType = sourceType




def getEventObjects(jsonPath: str, sourceType: SourceTypes) -> [EventKernel]:
    eventSchema: dict = None
    with open(jsonPath, "r") as f:
        eventSchema = json.load(f)
    
    eventKernels: [EventKernel] = []
    for key, event in eventSchema.items():
        def noneIfNotPresent(x):
            return None if x not in event else event[x]
        
        
        eventAddress = None if "defaultLocation" not in event else EventParameters.Address(**event["defaultLocation"])
        category = None if "defaultCategory" not in event else EventParameters.Categories[event["defaultCategory"]]
        eventKernel = EventType(event["groupID"], noneIfNotPresent("title"), 
                            noneIfNotPresent("defaultDescription"), noneIfNotPresent("beginsOn"),
                            event["onlineAddress"], noneIfNotPresent("endsOn"), 
                            eventAddress, category, 
                            noneIfNotPresent("defaultTags"), EventParameters.MediaInput(event["defaultImageID"]))

        sourceIDs = noneIfNotPresent("sourceIDs")
        eventKernels.append(EventKernel(eventKernel, key, sourceIDs=sourceIDs, sourceType=sourceType))
    
    return eventKernels

def generateEventsFromStaticEventKernels(jsonPath: str, eventKernel: EventKernel) -> [EventType]:
    eventSchema: dict = None
    with open(jsonPath, "r") as f:
        eventSchema = json.load(f)
    
    times = eventSchema[eventKernel.eventKernelKey]["defaultTimes"]
    
    generatedEvents = []
    
    # startDate = datetime.fromisoformat(eventSchema[eventKernel.eventKernelKey]["startDate"])
    endDate = datetime.fromisoformat(eventSchema[eventKernel.eventKernelKey]["endDate"])
    now = datetime.utcnow().astimezone()
    
    if now.date() <= endDate.date():
        for t in times:
            event: EventType = copy.deepcopy(eventKernel.event)
            startTime = datetime.fromisoformat(t[0])
            endTime = datetime.fromisoformat(t[1])
            
            timeDifferenceWeeks = (now - startTime).days // 7 # Floor division that can result in week prior event
            
            startTime += timedelta(weeks=timeDifferenceWeeks)
            endTime += timedelta(weeks=timeDifferenceWeeks)
            
            if startTime < now:
                startTime += timedelta(weeks=1)
                endTime += timedelta(weeks=1)
                if startTime > endDate:
                    return []
            
            event.beginsOn = startTime.astimezone().isoformat()
            event.endsOn = endTime.astimezone().isoformat()
        
            generatedEvents.append(event)
        
        return generatedEvents
    
    logger.info(f"Static Event {eventKernel.eventKernelKey} Has Expired")
    return []
    
    












