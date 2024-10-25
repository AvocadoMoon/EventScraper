# EventScraper

A project dedicated to scrapping events and posting them on 
different platforms for searching. Unbinding posted events from any single platform to help illuminate what is locally happening.

## Docker (Recommended Method)
#### Env Variables
Mobilizon Related Variables:
- MOBILIZON_ENDPOINT: Graphql endpoint for your mobilizon instance

- MOBILIZON_EMAIL: User email

- MOBILIZON_PASSWORD: User password

OS Related Variables:
- USER_ID: User process ID for running the application

- GROUP_ID: Group process ID for running the application

Misc:
- RUNNER_SUBMISSION_JSON_PATH: Remote submission file that tells where to publish and what group packages to use for sources.

- SLACK_WEBHOOK: Slack token to give notifications on how the scraping process is going and whether any maintenance is required.

---
#### Docker Volumes
/app/config:[HOST DIR] -- The files needed within this config folder are "adc.json". This is the application default credentials required for accessing Google resources such as calendars. Please create your own google application, and store it's credentials here.
