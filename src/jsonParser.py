import json
import logging
import urllib.request

from src.logger import logger_name
from src.publishers.mobilizon.types import MobilizonEvent, EventParameters
from src.db_cache import SourceTypes
from datetime import datetime, timedelta
import copy

logger = logging.getLogger(logger_name)



class GroupEventsKernel:
    event: MobilizonEvent
    group_key: str
    event_sourceIDs: [str]
    sourceType: SourceTypes
    
    def __init__(self, event, event_key, source_ids, source_type):
        self.event = event
        self.event_sourceIDs = source_ids
        self.group_key = event_key
        self.sourceType = source_type




def get_event_objects(json_path: str, source_type: SourceTypes) -> [GroupEventsKernel]:
    event_schema: dict = None
    with urllib.request.urlopen(json_path) as f:
        event_schema = json.load(f)
    
    event_kernels: [GroupEventsKernel] = []
    for key, event in event_schema.items():
        def none_if_not_present(x):
            return None if x not in event else event[x]
        
        
        event_address = None if "defaultLocation" not in event else EventParameters.Address(**event["defaultLocation"])
        category = None if "defaultCategory" not in event else EventParameters.Categories[event["defaultCategory"]]
        event_kernel = MobilizonEvent(event["groupID"], none_if_not_present("title"),
                                     none_if_not_present("defaultDescription"), none_if_not_present("beginsOn"),
                                     event["onlineAddress"], none_if_not_present("endsOn"),
                                     event_address, category,
                                     none_if_not_present("defaultTags"), EventParameters.MediaInput(event["defaultImageID"]))

        source_ids = none_if_not_present("sourceIDs")
        event_kernels.append(GroupEventsKernel(event_kernel, key, source_ids=source_ids, source_type=source_type))
    
    return event_kernels

def generate_events_from_static_event_kernels(json_path: str, event_kernel: GroupEventsKernel) -> [MobilizonEvent]:
    event_schema: dict = None
    with urllib.request.urlopen(json_path) as f:
        event_schema = json.load(f)
    
    times = event_schema[event_kernel.group_key]["defaultTimes"]
    
    generated_events = []
    
    # startDate = datetime.fromisoformat(eventSchema[eventKernel.eventKernelKey]["startDate"])
    end_date = datetime.fromisoformat(event_schema[event_kernel.group_key]["endDate"])
    now = datetime.utcnow().astimezone()
    
    if now.date() <= end_date.date():
        for t in times:
            event: MobilizonEvent = copy.deepcopy(event_kernel.event)
            start_time = datetime.fromisoformat(t[0])
            end_time = datetime.fromisoformat(t[1])
            
            time_difference_weeks = (now - start_time).days // 7 # Floor division that can result in week prior event
            
            start_time += timedelta(weeks=time_difference_weeks)
            end_time += timedelta(weeks=time_difference_weeks)
            
            if start_time < now:
                start_time += timedelta(weeks=1)
                end_time += timedelta(weeks=1)
                if start_time > end_date:
                    return []
            
            event.beginsOn = start_time.astimezone().isoformat()
            event.endsOn = end_time.astimezone().isoformat()
        
            generated_events.append(event)
        
        return generated_events
    
    logger.info(f"Static Event {event_kernel.group_key} Has Expired")
    return []
    
    












