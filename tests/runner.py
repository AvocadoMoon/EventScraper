from src.db_cache import SQLiteDB, UploadedEventRow
from src.Runner import Runner
import sqlite3
import os
import unittest
import logging
from src.logger import setup_custom_logger

# TODO: Test the entire runner interaction that it executes

class TestRunner(unittest.TestCase):
    runner: Runner
    
    @classmethod
    def setUpClass(cls):
        cls.runner = Runner(True)
    
    @classmethod
    def tearDownClass(cls):
        cls.runner.clean_up()
    
    def test_Runners_Idempotency(self):
        
        self.runner.run()
        db_results = self.runner.cache_db.selectAllFromUploadTable().fetchall()
        
        self.runner.run()
        second_db_results = self.runner.cache_db.selectAllFromUploadTable().fetchall()
            
        self.assertEqual(len(db_results), len(second_db_results))
        
        for row in range(len(db_results)):
            for column in range(len(db_results[row])):
                self.assertEqual(db_results[row][column], second_db_results[row][column])
        

if __name__ == "__main__":
    setup_custom_logger(logging.INFO)
    unittest.main()