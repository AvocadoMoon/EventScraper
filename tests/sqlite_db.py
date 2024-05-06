from src.drivers.mobilizon.db_cache import SQLiteDB, UploadedEventRow
import sqlite3
import os
import unittest

# TODO: Test getting the last event uploaded for a specific group

class EventTableTest(unittest.TestCase):
    def test_UploadedEventsTable(self):
        group1: [UploadedEventRow] = [
            UploadedEventRow("uuid1", "id1", "title1", "2022-05-04T10:00:00-04:00", "group1"),
            UploadedEventRow("uuid2", "id1", "title1", "2022-05-04T10:00:00-04:00", "group1"),
            UploadedEventRow("uuid3", "id1", "title1", "2022-05-04T10:00:00-04:00", "group1"),
        ]
        group2: [UploadedEventRow] = [
            UploadedEventRow("uuid4", "id1", "title1", "2024-05-04T10:00:00-04:00", "group2"),
            UploadedEventRow("uuid5", "id1", "title1", "2024-05-04T10:00:00-04:00", "group2"),
            UploadedEventRow("uuid6", "id1", "title1", "2024-05-04T10:00:00-04:00", "group2"),
            UploadedEventRow("uuid7", "id1", "title1", "2024-05-04T10:00:00-04:00", "group2")
        ]
        
        group3: [UploadedEventRow] = [
            UploadedEventRow("uuid8", "id1", "title1", "2024-05-04T10:00:00-04:00", "group3")
        ]
        
        group3Listize = ["uuid8", "id1", "title1", "2024-05-04T10:00:00-04:00", "group3"]
        
        db = SQLiteDB()
        db.connectAndInitializeDB()
        
        db.insertUploadedEvent(group1)
        query = db.selectAllFromTable().fetchall()
        self.assertEqual(len(query), len(group1), "Ensure group 1 has been fully inserted")
        
        query = db.selectGroupFromTable("group1").fetchall()
        self.assertEqual(len(query), len(group1), "Getting groups work when alone")
        
        
        db.insertUploadedEvent(group2)
        query = db.selectAllFromTable().fetchall()
        self.assertEqual(len(query), (len(group1) + len(group2)), "Inserting another unique group ensures all are in")
        
        query = db.selectGroupFromTable("group2").fetchall()
        self.assertEqual(len(query), len(group2), "Ensure only selected group is taken when there's multiple groups")
        for row in query:
            self.assertEqual(row[4], "group2")
        
        db.deleteAllMonthOldEvents()
        query = db.selectAllFromTable().fetchall()
        self.assertEqual(len(query), len(group2), "Ensure that all old events are deleted and only new ones are left")
        for row in query:
            self.assertEqual(row[4], "group2")
        
        # Ensure only Unique UUIDs are inserted
        self.assertRaises(sqlite3.IntegrityError, db.insertUploadedEvent, group2)
        
        db.insertUploadedEvent(group3)
        query = db.selectGroupFromTable("group3").fetchone()
        for k in range(4):
            self.assertEqual(query[k], group3Listize[k], "Every item is accounted for")
        
        os.remove(f"{os.getcwd()}/event_cache.db")
        
if __name__ == "__main__":
    unittest.main()