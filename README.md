# EventScraper

A project dedicated to scrapping events and posting them on 
different platforms for searching. Unbinding posted events from any single platform to help illuminate what is locally happening.

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
