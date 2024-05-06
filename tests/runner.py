from src.drivers.mobilizon.db_cache import SQLiteDB, UploadedEventRow
from src.Runner import Runner
import sqlite3
import os
import unittest

# TODO: Test the entire runner interaction that it executes

class TestRunner(unittest.TestCase):
    runner: Runner
    
    @classmethod
    def setUpClass(cls):
        cls.runner = Runner(True)
    
    @classmethod
    def tearDownClass(cls):
        cls.runner.cleanUp()
    
    def test_Runners_Idempotency(self):
        
        self.runner.getGCalEventsAndUploadThem()
        db_results = self.runner.cache_db.selectAllFromTable().fetchall()
        
        self.runner.getGCalEventsAndUploadThem()
        second_db_results = self.runner.cache_db.selectAllFromTable().fetchall()
        
        self.assertEqual(len(db_results), len(second_db_results))
        
        for row in range(len(db_results)):
            for column in range(len(db_results[row])):
                self.assertEqual(db_results[row][column], second_db_results[row][column])
        

if __name__ == "__main__":
    unittest.main()