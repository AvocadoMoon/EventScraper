from drivers.mobilizon.mobilizon import MobilizonAPI
from drivers.mobilizon.mobilizon_types import EventParameters, EventType
import datetime
from datetime import timezone
import json
import os


# TO DO: Fix location

if __name__ == "__main__":
    endpoint = "https://ctgrassroots.org/graphiql"
    secrets: dict = None
    with open(f"{os.getcwd()}/src/secrets.json", "r") as f:
        secrets = json.load(f)
    mobilizonAPI = MobilizonAPI(endpoint, secrets["email"], secrets["password"])
    # Time object requires timeZone
    beginsOn = datetime.datetime(2024, 7, 7, 14, 35, tzinfo=timezone.utc)
    endsOn = datetime.datetime(2024, 7, 7, 17, 45, tzinfo=timezone.utc)
    cafe9Local = EventParameters.Address(locality="New Haven", 
                                         postalCode="CT 06510", street="250 State St", 
                                         country="USA")
    
    # print(mobilizonAPI.getActors())
    testEvent = EventType(14, "Test93", "Test description", beginsOn.isoformat(), "https://www.cafenine.com/",
        endsOn.isoformat(), cafe9Local, category=EventParameters.Categories.book_clubs)
    mobilizonAPI.bot_created_event(testEvent)
    # with open("//home/zek/Documents/Code/CTEventScraper/src/Duck.jpg", "rb") as f:
    #     params = {"file": f}
    #     print(mobilizonAPI.upload_file("Duck", f))
    mobilizonAPI.logout()
    print("Login and out")
