import logging
import unittest

from src.Runner import runner
from src.db_cache import SQLiteDB, ScraperTypes
from src.parser.jsonParser import get_group_package, get_runner_submission
from src.parser.types import GroupEventsKernel, RunnerSubmission
from src.logger import setup_custom_logger
from src.publishers.mobilizon.uploader import MobilizonUploader
from src.scrapers.statics.scraper import StaticScraper


# TODO: Test the entire runner interaction that it executes

class TestRunner(unittest.TestCase):

    def test_runners_insertions_correctness(self):
        cache_db: SQLiteDB = SQLiteDB(in_memory_sq_lite=True)
        submission = get_runner_submission(True, cache_db,
                                           "https://kernels.ctgrassroots.org/test-json/test-submission.json")
        runner(submission)
        db_results = cache_db.select_all_from_upload_table().fetchall()
        stonington_results = db_results[0]
        self.assertEqual("Stonington Farmers Market", stonington_results[2], "Title")
        self.assertEqual(25, stonington_results[4], "Group ID")
        self.assertEqual("Stonington", stonington_results[5], "Group Name")
        stamford_results = db_results[1]
        self.assertEqual("Stamford Downtown Farmers Market", stamford_results[2], "Title")
        self.assertEqual(25, stamford_results[4], "Group ID")
        self.assertEqual("Stamford", stamford_results[5], "Group Name")

        event_source_results = cache_db.select_all_from_event_source_table().fetchall()
        stonington_results = event_source_results[0]
        self.assertEqual("https://www.sviastonington.org/farmers-market",stonington_results[1], "Online Source")
        self.assertEqual("Stonington", stonington_results[2], "Source Name")
        self.assertEqual("JSON", stonington_results[3], "Source Type")
        stamford_results = event_source_results[1]
        self.assertEqual("http://stamford-downtown.com/events/farmers-market/", stamford_results[1], "Online Source")
        self.assertEqual("Stamford", stamford_results[2], "Source Name")
        self.assertEqual("JSON", stamford_results[3], "Source Type")


    def test_runners_idempotency_remote_submission(self):
        cache_db: SQLiteDB = SQLiteDB(in_memory_sq_lite=True)
        submission = get_runner_submission(True, cache_db,
"https://kernels.ctgrassroots.org/test-json/test-submission.json")

        runner(submission)
        cache_db = submission.cache_db
        db_results = cache_db.select_all_from_upload_table().fetchall()

        runner(submission)
        second_db_results = cache_db.select_all_from_upload_table().fetchall()

        self.assertTrue(len(db_results) > 1)
        self.assertEqual(len(db_results), len(second_db_results))

        for row in range(len(db_results)):
            for column in range(len(db_results[row])):
                self.assertEqual(db_results[row][column], second_db_results[row][column])

if __name__ == "__main__":
    setup_custom_logger(logging.INFO)
    unittest.main()