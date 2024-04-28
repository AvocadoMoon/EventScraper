from pydantic import BaseModel
from enum import Enum

class EventParameters:
    class Status(Enum):
        confirmed = "CONFIRMED"
        canceled = "CANCELED"
        tentative = "TENTATIVE"

    class Category(Enum):
        category = "CATEGORY"

    class Visibility(Enum):
        public = "PUBLIC"
    
    class JoinOptions(Enum):
        free = "FREE"
        invite = "INVITE"
        restricted = "RESTRICTED"

    class Address(BaseModel):
        """Address object that Mobilizon can utilize

        Args:
            geom: State
            locality: Town
            postalCode: ZipCode
            street: Street
            country: Country
        """
        geom: str = None # State
        locality: str  # Town
        postalCode: str # ZipCode
        street: str # Street
        country: str # 
    
    class MediaInput(BaseModel):
        media_id: int = None
    
    
        


class EventType(BaseModel):
    organizerActorId: int = 0
    attributedToId: int = 0
    title: str = ""
    description: str = None
    beginsOn: str = '"2020-10-29T00:00:00+01:00"'
    endsOn: str = None
    status: EventParameters.Status = EventParameters.Status.confirmed
    visibility: EventParameters.Visibility = EventParameters.Visibility.public
    joinOptions: EventParameters.JoinOptions = EventParameters.JoinOptions.free
    draft: str = None
    tags: list[str] = []
    picture: EventParameters.MediaInput = None # https://github.com/framasoft/mobilizon/blob/main/lib/graphql/schema/media.ex
    onlineAddress: str = None
    phoneAddress: str = None
    category: str = None
    physicalAddress: EventParameters.Address = None
    # options: dict = {}
    contacts: str = None

class Actor(BaseModel):
    id: int
    name: str
    preferredUsername: str
    type: str
    url: str
    
# print(isinstance(EventParameters.MediaInput(), (BaseModel)))


