from pydantic import BaseModel

class EventParameters:
    class EventStatus:
        confirmed = "CONFIRMED"
        canceled = "CANCELED"
        tentative = "TENTATIVE"

    class EventCategory:
        category = "CATEGORY"

    class EventVisibility:
        public = "PUBLIC"
    
    class JoinOptions:
        free = "FREE"
        invite = "INVITE"
        restricted = "RESTRICTED"

    class EventAddress(BaseModel):
        geom: str = 'null'
        locality: str  = 'null'  # Town
        postalCode: str = 'null'
        street: str = 'null'
        country: str = 'null'


class EventType(BaseModel):
    organizerActorId: int
    attributedToId: int
    title: str
    description: str = 'null'
    beginsOn: str = None
    endsOn: str = None
    status: str = EventParameters.EventStatus.confirmed
    visibility: str = EventParameters.EventVisibility.public
    joinOptions: str = EventParameters.JoinOptions.free
    draft: str = "false"
    tags: list[str] = []
    picture: str = None # https://github.com/framasoft/mobilizon/blob/main/lib/graphql/schema/media.ex
    onlineAddress: str = None
    phoneAddress: str = None
    category: str = None
    physicalAddress: EventParameters.EventAddress = EventParameters.EventAddress()
    # options: dict = {}
    contacts: str = None

class Actor(BaseModel):
    id: int
    name: str
    preferredUsername: str
    type: str
    url: str
