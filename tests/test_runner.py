import logging
import unittest
from math import trunc

from src.Runner import RunnerSubmission, runner
from src.db_cache import SQLiteDB, ScraperTypes
from src.jsonParser import get_group_kernels, get_scrapers_and_publishers
from src.scrapers.abc_scraper import GroupEventsKernel
from src.logger import setup_custom_logger
from src.publishers.mobilizon.uploader import MobilizonUploader
from src.scrapers.statics.scraper import StaticScraper


# TODO: Test the entire runner interaction that it executes

class TestRunner(unittest.TestCase):
    
    def _Runners_Idempotency(self, publishers, cache_db):
        submission: RunnerSubmission = RunnerSubmission(cache_db, publishers,True)
        runner(submission)
        db_results = cache_db.select_all_from_upload_table().fetchall()
        
        runner(submission)
        second_db_results = cache_db.select_all_from_upload_table().fetchall()
            
        self.assertEqual(len(db_results), len(second_db_results))
        
        for row in range(len(db_results)):
            for column in range(len(db_results[row])):
                self.assertEqual(db_results[row][column], second_db_results[row][column])

    def test_runners_idempotency(self):
        cache_db: SQLiteDB = SQLiteDB(in_memory_sq_lite=True)
        farmers_market: [GroupEventsKernel] = get_group_kernels(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/farmers_market.json",
            ScraperTypes.json)
        publishers = {
            MobilizonUploader(True, cache_db): [
                (StaticScraper(cache_db), farmers_market)
            ]
        }
        self._Runners_Idempotency(publishers, cache_db)

    def test_runners_idempotency_remote_submission(self):
        cache_db: SQLiteDB = SQLiteDB(in_memory_sq_lite=True)
        get_scrapers_and_publishers(True, cache_db,
                                    "https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/Scraper%20Submission/farming_only.json")

if __name__ == "__main__":
    setup_custom_logger(logging.INFO)
    unittest.main()