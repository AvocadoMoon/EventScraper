from src.publishers.mobilizon import MobilizonAPI
from src.publishers.mobilizon import EventParameters, EventType
from src.db_cache import UploadedEventRow, SQLiteDB, UploadSource, ScraperTypes
from src.scrapers.google_calendar.api import GCalAPI
from datetime import timezone, timedelta, datetime
import json
import os
from geopy.geocoders import Nominatim
import logging
from src.logger import setup_custom_logger

endpoint = "https://ctgrassroots.org/graphiql"
secrets: dict = None
with open(f"{os.getcwd()}/src/secrets.json", "r") as f:
    secrets = json.load(f)

def manualTestCreation():
    

    mobilizonAPI = MobilizonAPI(endpoint, secrets["email"], secrets["password"])
    # Time object requires timeZone
    beginsOn = datetime(2024, 7, 7, 14, 35, tzinfo=timezone.utc)
    endsOn = datetime(2024, 7, 7, 17, 45, tzinfo=timezone.utc)
    geo_locator = Nominatim(user_agent="manual test creation")
    location = geo_locator.geocode("250 State St, New Haven, CT 06510").raw
    geom = f"{location['lon']};{location['lat']}"
    print(geom)
    cafe9Local = EventParameters.Address(locality="New Haven", 
                                         postalCode="06510", street="250 State St", 
                                         country="United States", geom=geom,
                                         originId=f"nominatim:{location['place_id']}",
                                         type=location['addresstype'])
    
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
    google_calendar_api = GCalAPI()
    google_calendars: dict = None
    with open(f"{os.getcwd()}/src/scrapers/GCal.json", "r") as f:
        google_calendars = json.load(f)

    bsbco = google_calendars["Bradley Street Bike Co-Op"]
    exampleTimeOffset = datetime.utcnow() + timedelta(days=3)
    exampleTimeOffset = exampleTimeOffset.isoformat() + "Z"
    db = SQLiteDB(True)
    allEvents = google_calendar_api.getAllEventsAWeekFromNow(
        calendarDict=bsbco, calendarId=bsbco["googleIDs"][0], 
        checkCacheFunction=db.entry_already_in_cache)
    
    if(printEvents):
        for event in allEvents:
            print(f"Start: {event.beginsOn}, End: {event.endsOn}, Title: {event.title}\nDescription: {event.description}, Location: {None if event.physicalAddress is None else event.physicalAddress.locality}")

    return allEvents


def manualTestCacheDB():
    allEvents: [UploadedEventRow] = [
        UploadedEventRow("uuid1", "id1", "title1", "2022-05-05T16:00:00-04:00", "2", "group2"),
        UploadedEventRow("uuid5", "id1", "title1", "2022-05-05T10:00:00-04:00", "2", "group2"),
        UploadedEventRow("uuid3", "id1", "title1", "2022-05-04T10:00:00-04:00", "2", "group2")
    ]
    eventSources: [UploadSource] = [
        UploadSource("uuid1", "website", "123", ScraperTypes.gCal),
        UploadSource("uuid5", "website", "123", ScraperTypes.gCal),
        UploadSource("uuid3", "website", "123", ScraperTypes.gCal)
    ]
    db = SQLiteDB(True)
    for k in range(len(allEvents)):
        db.insert_uploaded_event(allEvents[k], eventSources[k])
    # print(db.selectAllFromTable().fetchall())
    print(db.get_last_event_date_for_source_id("123").isoformat())
    db.close()

def getEventBotInfo():
    mobilizonAPI = MobilizonAPI(endpoint, secrets["email"], secrets["password"])
    print(mobilizonAPI.getActors())
    print(mobilizonAPI.getGroups())
    mobilizonAPI.logout()

def _getAddressInfo():
    calendar_locations = {
        "Cafe Nine": "250 State St, New Haven, CT 06510",
        "BSBCO": "138 Bradley St, New Haven, CT 06511",
        "Hartford Jazz Society": "56 Arbor St, Hartford, CT 06106",
        "Healing Meals": "140 Nod Rd, Simsbury, CT 06070",
        "The Institute Library": "847 Chapel St, New Haven, CT 06510",
        "Elm City Games": "71 Orange St, New Haven, CT 06510",
        "New Haven Library": "133 Elm St, New Haven, CT 06510",
        "Hartford Library": "500 Main St, Hartford, CT 06103",
        "WBT": "105 Whitney Ave, New Haven, CT 06510"
    }
    geo_locator = Nominatim(user_agent="test nominatim")
    for key, value in calendar_locations.items():
        location = geo_locator.geocode(value)
        print(key, location.raw)
    


if __name__ == "__main__":
    setup_custom_logger(logging.DEBUG)
    # manualTestCreation()
    # manualTestGoogleCalendar(False)
    # manualTestCacheDB()
    # getEventBotInfo()
    # _getAddressInfo()
    
    
    
    pass

