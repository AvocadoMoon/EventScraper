from pydantic import BaseModel
from abc import ABC, abstractproperty
import datetime
from enum import Enum

class EventType(BaseModel):
  organizerActorId: int
  attributedToId: int
  title: str 
  description: str 
  beginsOn: str
  endsOn: str 
  status: EventParameters.EventStatus 
  visibility: str 
  joinOptions: str 
  draft: bool
  tags: [str]
  picture: str #https://github.com/framasoft/mobilizon/blob/main/lib/graphql/schema/media.ex
  onlineAddress: str
  phoneAddress: str
  category: str
  physicalAddress: EventParameters.EventAddress
  options: dict
  contacts: str


class EventParameters:
  class EventStatus(Enum):
    confirmed: "CONFIRMED"
    canceled: "CANCELED"
    tentative: "TENTATIVE"
  class EventCategory(Enum):
    category: "CATEGORY"
  class EventVisibility(Enum):
    public: "PUBLIC"
  class EventAddress(BaseModel):
    geom: str
    locality: str # Town
    postalCode: str
    street: str
    country: str


