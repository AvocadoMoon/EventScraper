import unittest

from src.db_cache import ScraperTypes
from src.parser.jsonParser import get_group_package, get_runner_submission
from src.publishers.mobilizon.uploader import MobilizonUploader
from src.parser.types import GroupEventsKernel, GroupPackage, RunnerSubmission
from src.scrapers.google_calendar.scraper import GoogleCalendarScraper
from src.scrapers.statics.scraper import StaticScraper


class TestJSONParser(unittest.TestCase):

    def test_gcal_event_kernel(self):
        google_calendars: GroupPackage = get_group_package(
            f"https://kernels.ctgrassroots.org/Group%20Packages/libraries.json",
        )
        first_group: GroupEventsKernel = google_calendars.scraper_type_and_kernels[ScraperTypes.GOOGLE_CAL][0]

        self.assertEqual("New Haven Library", first_group.group_name)
        self.assertEqual(ScraperTypes.GOOGLE_CAL, first_group.scraper_type)
        self.assertEqual("8qf27rmmeun7mat412odluuha11umbhm@import.calendar.google.com", first_group.calendar_ids[0])
        self.assertEqual(22, first_group.event_template.attributedToId)  # group ID
        self.assertEqual("family_education", first_group.event_template.category.name)
        self.assertEqual("93", first_group.event_template.picture.mediaId)


    def test_farmers_event_kernel(self):
        farmers_market: GroupPackage = get_group_package(
            f"https://kernels.ctgrassroots.org/Group%20Packages/farmers_market.json",
        )

        first_group: GroupEventsKernel = farmers_market.scraper_type_and_kernels[ScraperTypes.STATIC][0]

        self.assertEqual("Stonington",first_group.group_name)
        self.assertEqual(ScraperTypes.STATIC, first_group.scraper_type)
        self.assertEqual("Stonington Farmers Market", first_group.calendar_ids[0])
        self.assertEqual(25, first_group.event_template.attributedToId) # group ID
        self.assertEqual("food_drink", first_group.event_template.category.name)
        self.assertEqual("96", first_group.event_template.picture.mediaId)

    def test_runner_submission_json(self):
        google_calendars: GroupPackage = get_group_package(
            f"https://kernels.ctgrassroots.org/Group%20Packages/misc.json",
        )
        farmers_market: GroupPackage = get_group_package(
            f"https://kernels.ctgrassroots.org/Group%20Packages/farmers_market.json",
        )

        runner_submission: RunnerSubmission = get_runner_submission(True, None,
                                                                         "https://kernels.ctgrassroots.org/Scraper%20Submission/include_everything.json")

        mobilizon_publisher = list(runner_submission.publishers.keys())[0]
        group_packages = list(runner_submission.publishers.values())[0]

        self.assertIsInstance(mobilizon_publisher, MobilizonUploader, "Expected Mobilizon Uploader")
        self.assertIsInstance(runner_submission.respective_scrapers[ScraperTypes.GOOGLE_CAL],
                              GoogleCalendarScraper, "Expected Calendar Scraper")
        self.assertIsInstance(runner_submission.respective_scrapers[ScraperTypes.STATIC],
                              StaticScraper, "Expected Static Scraper")

        static = group_packages[2].scraper_type_and_kernels[ScraperTypes.STATIC]
        for i in range(len(static)):
            self.assertEqual(farmers_market.scraper_type_and_kernels[ScraperTypes.STATIC][i],
                             static[i])

if __name__ == '__main__':
    unittest.main()
