import unittest

from src.db_cache import ScraperTypes
from src.jsonParser import get_group_kernels, get_scrapers_and_publishers
from src.publishers.abc_publisher import Publisher
from src.publishers.mobilizon.uploader import MobilizonUploader
from src.scrapers.abc_scraper import Scraper, GroupEventsKernel
from src.scrapers.google_calendar.scraper import GoogleCalendarScraper
from src.scrapers.statics.scraper import StaticScraper


class TestJSONParser(unittest.TestCase):

    def test_gcal_event_kernel(self):
        google_calendars: [GroupEventsKernel] = get_group_kernels(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/Scraper%20Kernels/Google%20Calendar/gcal.json",
            ScraperTypes.GOOGLE_CAL
        )
        first_group: GroupEventsKernel = google_calendars[0]

        self.assertEqual("New Haven Library", first_group.group_name)
        self.assertEqual(ScraperTypes.GOOGLE_CAL, first_group.scraper_type)
        self.assertEqual("8qf27rmmeun7mat412odluuha11umbhm@import.calendar.google.com", first_group.calendar_ids[0])
        self.assertEqual(22, first_group.event_template.attributedToId)  # group ID
        self.assertEqual("family_education", first_group.event_template.category.name)
        self.assertEqual("93", first_group.event_template.picture.mediaId)


    def test_farmers_event_kernel(self):
        farmers_market: [GroupEventsKernel] = get_group_kernels(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/Scraper%20Kernels/Static/farmers_market.json",
            ScraperTypes.STATIC
        )

        first_group: GroupEventsKernel = farmers_market[0]

        self.assertEqual("Stonington",first_group.group_name)
        self.assertEqual(ScraperTypes.STATIC, first_group.scraper_type)
        self.assertEqual("Stonington Farmers Market", first_group.calendar_ids[0])
        self.assertEqual(25, first_group.event_template.attributedToId) # group ID
        self.assertEqual("food_drink", first_group.event_template.category.name)
        self.assertEqual("96", first_group.event_template.picture.mediaId)

    def test_reading_scraper_and_publisher_json(self):
        google_calendars: [GroupEventsKernel] = get_group_kernels(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/Scraper%20Kernels/Google%20Calendar/gcal.json",
            ScraperTypes.GOOGLE_CAL
        )
        farmers_market: [GroupEventsKernel] = get_group_kernels(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/Scraper%20Kernels/Static/farmers_market.json",
            ScraperTypes.STATIC
        )
        # expected: {Publisher: [(Scraper, [GroupEventsKernel])]} = {
        #     MobilizonUploader(True, None) : [
        #         (GoogleCalendarScraper(None), google_calendars),
        #         (StaticScraper(None), farmers_market)
        #     ]
        # }
        test_scraper_publisher: {Publisher: [(Scraper, [GroupEventsKernel])]} = get_scrapers_and_publishers(True, None,
                                                                                                            "https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/Scraper%20Submission/include_everything.json")
        first_publisher = list(test_scraper_publisher.keys())[0]
        gcal = test_scraper_publisher[first_publisher][0]
        static = test_scraper_publisher[first_publisher][1]
        self.assertIsInstance(first_publisher, MobilizonUploader, "Expected Mobilizon Uploader")
        self.assertIsInstance(gcal[0], GoogleCalendarScraper, "Expected Calendar Scraper")
        self.assertIsInstance(static[0], StaticScraper, "Expected Static Scraper")

        for i in range(len(gcal[1])):
            self.assertEqual(google_calendars[i], gcal[1][i])
        for i in range(len(static[1])):
            self.assertEqual(farmers_market[i], static[1][i])

if __name__ == '__main__':
    unittest.main()
