
from abc import ABC

from pydantic import BaseModel


class EventType(BaseModel):
    title: str = ""
    description: str = None
    beginsOn: str = "2020-10-29T00:00:00+01:00"
    endsOn: str = None
    picture = None
    url: str = None
    organizers: str = None
    phoneAddress: str = None
    physicalAddress = None
    eventTicket = None







