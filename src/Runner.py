import datetime
import logging
import os
import time

from requests.exceptions import HTTPError
from slack_sdk.webhook import WebhookClient

from src.db_cache import SQLiteDB
from src.parser.jsonParser import get_runner_submission
from src.logger import logger_name, setup_custom_logger
from src.publishers.abc_publisher import Publisher
from src.scrapers.abc_scraper import Scraper
from src.parser.types import GroupEventsKernel, GroupPackage, RunnerSubmission, EventsToUploadFromCalendarID
from src.scrapers.google_calendar.api import ExpiredToken

logger = logging.getLogger(logger_name)


def runner(runner_submission: RunnerSubmission):
    continue_scraping = True
    num_retries = 0

    while continue_scraping and num_retries < 5:
        try:
            submitted_publishers: {Publisher: [GroupPackage]} = runner_submission.publishers
            for publisher in submitted_publishers.keys():
                publisher: Publisher
                publisher.connect()
                group_package: GroupPackage
                for group_package in submitted_publishers[publisher]:
                    logger.info(f"Reading Group Package: {group_package.package_name}")

                    for scraper_type in group_package.scraper_type_and_kernels.keys():
                        scraper: Scraper = runner_submission.respective_scrapers[scraper_type]
                        scraper.connect_to_source()
                        group_event_kernels: [GroupEventsKernel] = group_package.scraper_type_and_kernels[scraper_type]
                        for event_kernel in group_event_kernels:
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

        test_mode = False if "TEST_MODE" not in os.environ else True
        cache_db: SQLiteDB = SQLiteDB(test_mode)
        submission: RunnerSubmission = get_runner_submission(test_mode, cache_db)

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

