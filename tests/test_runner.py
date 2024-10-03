import logging
import unittest
from math import trunc

from src.Runner import RunnerSubmission, runner
from src.db_cache import SQLiteDB, SourceTypes
from src.jsonParser import GroupEventsKernel, get_event_objects
from src.logger import setup_custom_logger
from src.publishers.mobilizon.uploader import MobilizonUploader
from src.scrapers.statics.scraper import StaticScraper


# TODO: Test the entire runner interaction that it executes

class TestRunner(unittest.TestCase):
    
    def test_Runners_Idempotency(self):
        cache_db: SQLiteDB = SQLiteDB(inMemorySQLite=True)
        farmers_market: [GroupEventsKernel] = get_event_objects(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/farmers_market.json",
            SourceTypes.json)
        publishers = {
            MobilizonUploader(True, cache_db): [
                (StaticScraper(), farmers_market)
            ]
        }
        submission: RunnerSubmission = RunnerSubmission(cache_db, publishers,True)


        runner(submission)
        db_results = cache_db.selectAllFromUploadTable().fetchall()
        
        runner(submission)
        second_db_results = cache_db.selectAllFromUploadTable().fetchall()
            
        self.assertEqual(len(db_results), len(second_db_results))
        
        for row in range(len(db_results)):
            for column in range(len(db_results[row])):
                self.assertEqual(db_results[row][column], second_db_results[row][column])
        

if __name__ == "__main__":
    setup_custom_logger(logging.INFO)
    unittest.main()