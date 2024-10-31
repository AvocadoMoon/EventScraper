import os
import unittest

from src.db_cache import SQLiteDB, ScraperTypes
from src.parser.types import GroupEventsKernel, EventsToUploadFromCalendarID
from src.publishers.mobilizon.types import MobilizonEvent, EventParameters
from src.scrapers.ical.scraper import ICALScraper


class TestICALScraper(unittest.TestCase):
    def setUp(self):
        os.environ["TEST"] = str("True")

    def test_ical_scraper_correctness(self):
        cache_db = SQLiteDB(True)
        ical_scraper = ICALScraper(cache_db)

        test_event_template = MobilizonEvent(0, "Test Title", "Test description", "")
        test_kernel = GroupEventsKernel(test_event_template, "",
                            ["https://kernels.ctgrassroots.org/test-json/test.ical"],
                                        ScraperTypes.ICAL, "")

        retrieved: [EventsToUploadFromCalendarID] = ical_scraper.retrieve_from_source(test_kernel)
        event_to_upload : EventsToUploadFromCalendarID = retrieved[0]
        event: MobilizonEvent = event_to_upload.events[0]

        test_event = MobilizonEvent(0, 'Black-eyed Sally’s Jazz Jam', """Automatically scraped by Event Bot : 

Located in downtown Hartford, for the aficionado, musician, or the curious first-timer, Black Eyed Sally’s Jazz Jams are the best taste of live jazz in Hartford. Set in the southern juke joint atmosphere of Black-eyed Sally’s, these jam sessions will strike a chord as you hear what our local talent has to offer, with regular special appearances by big city jazz names. Experience the cool original music of the jam session while you enjoy the hot fierce cookin’ of Hartford’s favorite BBQ joint. 
After a long hiatus due to the pandemic, regularly scheduled jazz jams have returned to Black Eyed Sally’s every Wednesday. There will be a featured jazz ensemble followed by an open jam session. Bring your axe and be ready to jam! 
The music begins at 7:00 PM, jam session begins after 1st set. No cover charge most nights, under 21’s welcome. 
Presented by the Hartford Jazz Society and Neefjazz Entertainment""", '2024-10-30T23:00:00+00:00',
                                    physicalAddress=EventParameters.Address(geom='-72.6796498;41.7677107', locality=' Hartford', postalCode=' 06103', street=' 350 Asylum St.', country='United States', type=None, region=' CT', timezone='America/New_York', description='', originId=None),
                                    onlineAddress='https://hartfordjazzsociety.com/event/black-eyed-sallys-jazz-jam/2024-10-30/',
                                    endsOn='2024-10-31T02:00:00+00:00')

        self.assertEqual(test_event, event)

        event = event_to_upload.events[1]
        test_event = MobilizonEvent(0, 'Black-eyed Sally’s Jazz Jam', 'Automatically scraped by Event Bot : \n\n', '2024-10-30T23:00:00+00:00',
                                    onlineAddress='https://hartfordjazzsociety.com/event/black-eyed-sallys-jazz-jam/2024-10-30/',
                                    endsOn='2024-10-31T02:00:00+00:00')

        self.assertEqual(test_event, event)





if __name__ == '__main__':
    unittest.main()

