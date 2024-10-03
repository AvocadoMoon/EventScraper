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
    event_template: MobilizonEvent
    group_name: str
    calendar_ids: [str]
    sourceType: SourceTypes
    
    def __init__(self, event, group_name, calendar_ids, source_type):
        self.event_template = event
        self.calendar_ids = calendar_ids
        self.group_name = group_name
        self.sourceType = source_type




def get_event_objects(json_path: str, source_type: SourceTypes) -> [GroupEventsKernel]:
    group_schema: dict = None
    with urllib.request.urlopen(json_path) as f:
        group_schema = json.load(f)
    
    event_kernels: [GroupEventsKernel] = []
    for group_name, group_info in group_schema.items():
        def none_if_not_present(x):
            return None if x not in group_info else group_info[x]
        
        
        event_address = None if "defaultLocation" not in group_info else EventParameters.Address(**group_info["defaultLocation"])
        category = None if "defaultCategory" not in group_info else EventParameters.Categories[group_info["defaultCategory"]]
        event_kernel = MobilizonEvent(group_info["groupID"], none_if_not_present("title"),
                                     none_if_not_present("defaultDescription"), none_if_not_present("beginsOn"),
                                     group_info["onlineAddress"], none_if_not_present("endsOn"),
                                     event_address, category,
                                     none_if_not_present("defaultTags"), EventParameters.MediaInput(group_info["defaultImageID"]))

        calendar_ids = group_info["calendarIDs"]
        event_kernels.append(GroupEventsKernel(event_kernel, group_name, calendar_ids=calendar_ids, source_type=source_type))
    
    return event_kernels

def generate_events_from_static_event_kernels(json_path: str, event_kernel: GroupEventsKernel) -> [MobilizonEvent]:
    event_schema: dict = None
    with urllib.request.urlopen(json_path) as f:
        event_schema = json.load(f)
    
    times = event_schema[event_kernel.group_name]["defaultTimes"]
    
    generated_events = []
    
    # startDate = datetime.fromisoformat(eventSchema[eventKernel.eventKernelKey]["startDate"])
    end_date = datetime.fromisoformat(event_schema[event_kernel.group_name]["endDate"])
    now = datetime.utcnow().astimezone()
    
    if now.date() <= end_date.date():
        for t in times:
            event: MobilizonEvent = copy.deepcopy(event_kernel.event_template)
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
    
    logger.info(f"Static Event {event_kernel.group_name} Has Expired")
    return []
    
    












