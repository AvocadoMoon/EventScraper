# CTEventScraper

Project dedicated to scrapping events located within Connecticut and posting them on Mobilizon for searching. Help illuminate what is locally happening, and keep people informed on events to dedicate their time to. 

### Current Sources

- Google Calendar
    - Hartford Jazz Society
    - WBT
    - Elm City Games
    - Downtown New Haven
    - Bradely Street Bike-Coop
    - Healing Meals
    - Save the Sound
    - New Haven Library
    - Hartford Public Library


## Docker
---
#### Docker Env Variables
MOBILIZON_ENDPOINT: Graphql endpoint for your mobilizon instance
MOBILIZON_EMAIL: User email
MOBILIZON_PASSWORD: User password

USER_ID: User process ID for running the application
GROUP_ID: Group process ID for running the application

---
#### Docker Volumes
/app/config:[HOST DIR] -- The files needed within this config are "adc.json". This is the application default credentials required for accessing google resources such as calendar. Please create your own google application, and store it's credentials here.
