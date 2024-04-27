from pydantic import BaseModel

class EventParameters:
    class Status:
        confirmed = "CONFIRMED"
        canceled = "CANCELED"
        tentative = "TENTATIVE"

    class Category:
        category = "CATEGORY"

    class Visibility:
        public = "PUBLIC"
    
    class JoinOptions:
        free = "FREE"
        invite = "INVITE"
        restricted = "RESTRICTED"

    class Address(BaseModel):
        geom: str = None
        locality: str  = None  # Town
        postalCode: str = None
        street: str = None
        country: str = None
    
    class MediaInput(BaseModel):
        media_id: int = None
    
    
        


class EventType(BaseModel):
    organizerActorId: int = 0
    attributedToId: int = 0
    title: str = ""
    description: str = None
    beginsOn: str = '"2020-10-29T00:00:00+01:00"'
    endsOn: str = '"2022-03-31T23:59:59+02:00"'
    status: str = EventParameters.Status.confirmed
    visibility: str = EventParameters.Visibility.public
    joinOptions: str = EventParameters.JoinOptions.free
    draft: str = "false"
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


