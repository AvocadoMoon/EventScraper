import json
import logging
from src.logger import logger_name
from src.mobilizon.mobilizon_types import EventType, EventParameters
from datetime import datetime, timedelta
import copy

logger = logging.getLogger(logger_name)



class EventKernel:
    event: EventType
    eventKernelKey: str
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

        sourceIDs = noneIfNotPresent("sourceIDs")
        eventKernels.append(EventKernel(eventKernel, key, sourceIDs=sourceIDs))
    
    return eventKernels

def generateEventsFromStaticEventKernels(jsonPath: str, eventKernel: EventKernel) -> [EventType]:
    eventSchema: dict = None
    with open(jsonPath, "r") as f:
        eventSchema = json.load(f)
    
    times = eventSchema["defaultTimes"]
    
    generatedEvents = []
    
    startDate = datetime.fromisoformat(eventSchema["startDate"])
    endDate = datetime.fromisoformat(eventSchema["endDate"])
    now = datetime.utcnow()
    
    if startDate.date() <= now.date() <= endDate.date():
        for t in times:
            event: EventType = copy.deepcopy(eventKernel.event)
            startTime = datetime.fromisoformat(t[0])
            endTime = datetime.fromisoformat(t[1])
            
            timeDifferenceWeeks = (now - startTime).days % 7
            
            startTime += timedelta(weeks=timeDifferenceWeeks)
            endTime += timedelta(weeks=timeDifferenceWeeks)
            
            event.beginsOn = startTime.astimezone().isoformat()
            event.endsOn = endTime.astimezone().isoformat()
        
            generatedEvents.append(event)
        
        return generatedEvents
    
    logger.info(f"Static Event {eventKernel.eventKernelKey} Has Expired")
    return []
    
    












