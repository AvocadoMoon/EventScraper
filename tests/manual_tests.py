from src.drivers.mobilizon.mobilizon import MobilizonAPI
from src.drivers.mobilizon.mobilizon_types import EventParameters, EventType
from src.drivers.mobilizon.db_cache import UploadedEventRow, SQLiteDB
from src.website_scraper.google_calendar import GCalAPI
from datetime import timezone, timedelta, datetime
import json
import os


# TODO: Fix location 

endpoint = "https://ctgrassroots.org/graphiql"
secrets: dict = None
with open(f"{os.getcwd()}/src/secrets.json", "r") as f:
    secrets = json.load(f)

def manualTestCreation():
    

    mobilizonAPI = MobilizonAPI(endpoint, secrets["email"], secrets["password"])
    # Time object requires timeZone
    beginsOn = datetime(2024, 7, 7, 14, 35, tzinfo=timezone.utc)
    endsOn = datetime(2024, 7, 7, 17, 45, tzinfo=timezone.utc)
    cafe9Local = EventParameters.Address(locality="New Haven", 
                                         postalCode="CT 06510", street="250 State St", 
                                         country="USA")
    
    # print(mobilizonAPI.getActors())
    defaultImage = EventParameters.MediaInput(mediaId="87")
    testEvent = EventType(14, "Test93", "Test description", beginsOn.isoformat(), "https://www.cafenine.com/",
        endsOn.isoformat(), cafe9Local, category=EventParameters.Categories.book_clubs,
        picture=defaultImage)
    print(mobilizonAPI.bot_created_event(testEvent))
    # with open("//home/zek/Documents/Code/CTEventScraper/src/Duck.jpg", "rb") as f:
    #     params = {"file": f}
    #     print(mobilizonAPI.upload_file("Duck", f))
    mobilizonAPI.logout()
    print("Login and out")

def manualTestGoogleCalendar(printEvents:bool = False):
    publicCalenderIDs = ["bsbc.co_c4dt5esnmutedv7p3nu01aerhk@group.calendar.google.com",
                        "ctenvironment@gmail.com"]
    google_calendar_api = GCalAPI()

    exampleTimeOffset = datetime.utcnow() + timedelta(days=3)
    exampleTimeOffset = exampleTimeOffset.isoformat() + "Z"
    allEvents = []
    for k in publicCalenderIDs:
        allEvents.append(google_calendar_api.getAllEventsAWeekFromNow(k, 2, "3"))
    
    if(printEvents):
        for j in allEvents:
            for event in j:
                print(f"Start: {event.beginsOn}, End: {event.endsOn}, Title: {event.title}\nDescription: {event.description}, Location: {None if event.physicalAddress is None else event.physicalAddress.locality}")

    return allEvents


def manualTestCacheDB():
    allEvents: [UploadedEventRow] = [
        UploadedEventRow("uuid1", "id1", "title1", "2022-05-05T16:00:00-04:00", "2", "group2", "123"),
        UploadedEventRow("uuid5", "id1", "title1", "2022-05-05T10:00:00-04:00", "2", "group2", "123"),
        UploadedEventRow("uuid3", "id1", "title1", "2022-05-04T10:00:00-04:00", "2", "group2", "123")
    ]
    db = SQLiteDB(True)
    for k in allEvents:
        db.insertUploadedEvent(k)
    # print(db.selectAllFromTable().fetchall())
    print(db.getLastEventForCalendarID("123").isoformat())
    db.close()

def getEventBotInfo():
    mobilizonAPI = MobilizonAPI(endpoint, secrets["email"], secrets["password"])
    print(mobilizonAPI.getActors())
    print(mobilizonAPI.getGroups())
    mobilizonAPI.logout()


if __name__ == "__main__":
    
    # manualTestCreation()
    manualTestGoogleCalendar(True)
    # manualTestCacheDB()
    # getEventBotInfo()
    
    
    
    pass

