import datetime
import logging
import os
import time

from requests.exceptions import HTTPError
from slack_sdk.webhook import WebhookClient

from src.db_cache import SQLiteDB, ScraperTypes
from src.jsonParser import GroupEventsKernel, get_group_kernels
from src.logger import logger_name, setup_custom_logger
from src.publishers.abc_publisher import Publisher
from src.publishers.mobilizon.uploader import MobilizonUploader
from src.scrapers.abc_scraper import Scraper, EventsToUploadFromCalendarID
from src.scrapers.google_calendar.api import ExpiredToken
from src.scrapers.google_calendar.scraper import GoogleCalendarScraper
from src.scrapers.statics.scraper import StaticScraper

logger = logging.getLogger(logger_name)

class RunnerSubmission:
    def __init__(self, submitted_db: SQLiteDB,
                 submitted_publishers: {Publisher: [(Scraper, [GroupEventsKernel])]},
                 test: bool):
        self.cache_db = submitted_db
        self.test = test
        self.publishers = submitted_publishers



def runner(runner_submission: RunnerSubmission):
    continue_scraping = True
    num_retries = 0

    while continue_scraping and num_retries < 5:
        try:
            submitted_publishers: {Publisher: [(Scraper, [GroupEventsKernel])]} = runner_submission.publishers
            for publisher in submitted_publishers.keys():
                publisher: Publisher
                publisher.connect()
                scraper_and_kernel_list = submitted_publishers[publisher]
                for scraper_and_kernels in scraper_and_kernel_list:
                    scraper: Scraper = scraper_and_kernels[0]
                    scraper.connect_to_source()
                    event_kernels: [GroupEventsKernel] = scraper_and_kernels[1]

                    for event_kernel in event_kernels:
                        events: [EventsToUploadFromCalendarID] = scraper.retrieve_from_source(event_kernel)
                        publisher.upload(events)

                    scraper.close()
                publisher.close()

            continue_scraping = False
        except HTTPError as err:
            if err.response.status_code == 500 and err.response.message == 'Too many requests':
                num_retries += 1
                logger.warning("Going to sleep then retrying to scrape. Retry Num: " + num_retries)
                time.sleep(120)

def days_to_sleep(days):
    now = datetime.datetime.now()
    seconds_from_zero = (now.hour * 60 * 60)
    time_at_2am = 2 * 60 * 60
    time_to_sleep = time_at_2am
    if seconds_from_zero > time_at_2am:
        time_to_sleep = ((23 * 60 * 60) - seconds_from_zero) + time_at_2am
    else:
        time_to_sleep = time_at_2am - seconds_from_zero
    
    return time_to_sleep + (60 * 60 * 24 * days)


def produce_slack_message(color, title, text, priority):
    return {
            "color": color,
            "author_name": "CTEvent Scraper",
            "author_icon": "https://ctgrassroots.org/favicon.ico",
            "title": title,
            "title_link": "google.com",
            "text": text,
            "fields": [
                {
                    "title": "Priority",
                    "value": priority,
                    "short": "false"
                }
            ],
            "footer": "CTEvent Scraper",
        }


if __name__ == "__main__":
    setup_custom_logger(logging.INFO)
    logger.info("Scraper Started")
    sleeping = 2
    webhook = WebhookClient(os.environ.get("SLACK_WEBHOOK"))
    while True:
        #####################
        # Create Submission #
        #####################
        google_calendars: [GroupEventsKernel] = get_group_kernels(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/gcal.json", ScraperTypes.gCal)
        farmers_market: [GroupEventsKernel] = get_group_kernels(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/farmers_market.json",
            ScraperTypes.json)
        test_mode = False if "TEST_MODE" not in os.environ else True
        cache_db: SQLiteDB = SQLiteDB(test_mode)
        publishers = {
            MobilizonUploader(test_mode, cache_db): [
                (StaticScraper(), farmers_market),
                (GoogleCalendarScraper(cache_db), google_calendars)
            ]
        }
        submission: RunnerSubmission = RunnerSubmission(cache_db, publishers, False)

        ######################
        # Execute Submission #
        ######################
        timeToSleep = days_to_sleep(sleeping)
        logger.info("Scraping")
        try:
            runner(submission)
            logger.info("Sleeping " + str(sleeping) + " Days Until Next Scrape")
        except ExpiredToken:
            logger.warning("Expired token.json needs to be replaced")
            timeToSleep = days_to_sleep(1)
            logger.warning("Sleeping only 1 day")
            response = webhook.send(attachments=[
                produce_slack_message("#e6e209", "Expired Token", "Replace token.json", "Medium")
            ])
        
        except Exception as e:
            logger.error("Unknown Error")
            logger.error(e)
            logger.error("Going to Sleep for 7 days")
            webhook.send(attachments=[
                produce_slack_message("#ab1a13", "Event Scraper Unknown Error", "Check logs for error.", "High")
            ])
            timeToSleep = days_to_sleep(7)

        cache_db.close()
        time.sleep(timeToSleep)
    
    logger.info("Scraper Stopped")

