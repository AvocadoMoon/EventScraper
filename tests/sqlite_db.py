from src.db_cache import SQLiteDB, UploadedEventRow, UploadSource, SourceTypes
import sqlite3
import os
import unittest

# TODO: Test getting the last event uploaded for a specific group

class EventTableTest(unittest.TestCase):
    def test_UploadedEventsTable(self):
        
        group1Name = "groupName1"
        group2Name = "groupName2"
        sourceGroup1 = "source1"
        sourceGroup2 = "source2"
        
        group1: [UploadedEventRow] = [
            UploadedEventRow("uuid1", "id1", "title1", "2022-05-04T10:00:00-04:00", "gID1",group1Name),
            UploadedEventRow("uuid2", "id1", "title1", "2022-05-04T10:00:00-04:00", "gID1", group1Name),
            UploadedEventRow("uuid3", "id1", "title1", "2022-05-04T10:00:00-04:00", "gID1", group1Name),
        ]
        group1Source: [UploadSource] = [
            UploadSource("uuid1", "web", sourceGroup1, SourceTypes.gCal),
            UploadSource("uuid2", "web", sourceGroup1, SourceTypes.gCal),
            UploadSource("uuid3", "web", sourceGroup1, SourceTypes.gCal)

        ]
        
        group2: [UploadedEventRow] = [
            UploadedEventRow("uuid4", "id1", "title1", "2027-01-04T10:00:00-04:00", "gID2", group2Name),
            UploadedEventRow("uuid5", "id1", "title1", "2027-01-04T10:00:00-04:00", "gID2", group2Name),
            UploadedEventRow("uuid6", "id1", "title1", "2027-01-04T10:00:00-04:00", "gID2", group2Name),
            UploadedEventRow("uuid7", "id1", "title1", "2027-02-04T10:00:00-04:00", "gID2", group2Name)
        ]
        group2Source: [UploadSource] = [
            UploadSource("uuid4", "web", sourceGroup2, SourceTypes.json),
            UploadSource("uuid5", "web", sourceGroup2, SourceTypes.json),
            UploadSource("uuid6", "web", sourceGroup2, SourceTypes.json),
            UploadSource("uuid7", "web", sourceGroup2, SourceTypes.json)
        ]
        
        db = SQLiteDB(True)

        for k in range(len(group1)):
            db.insertUploadedEvent(group1[k], group1Source[k])        
        query = db.selectAllFromUploadTable().fetchall()
        self.assertEqual(len(query), len(group1), "Ensure group 1 has been fully inserted")
        
        query = db.selectAllRowsWithCalendarID(sourceGroup1).fetchall()
        self.assertEqual(len(query), len(group1), "Getting groups work when alone")
        
        for k in range(len(group2)):
            db.insertUploadedEvent(group2[k], group2Source[k])
        query = db.selectAllFromUploadTable().fetchall()
        self.assertEqual(len(query), (len(group1) + len(group2)), "Inserting another unique group ensures all are in")
        
        query = db.selectAllRowsWithCalendarID(sourceGroup2).fetchall()
        self.assertEqual(len(query), len(group2), "Ensure only selected group is taken when there's multiple groups")
        for row in query:
            self.assertEqual(row[7], sourceGroup2)
        
        db.deleteAllMonthOldEvents()
        query = db.selectAllFromUploadTable().fetchall()
        self.assertEqual(len(query), len(group2), "Ensure that all old events are deleted and only new ones are left")
        for row in query:
            self.assertEqual(row[5], group2Name)
        
        # Ensure only Unique UUIDs are inserted
        self.assertRaises(sqlite3.IntegrityError, db.insertUploadedEvent, group2[0], group2Source[0])
        
        for k in range(len(group2)):
            inCache = db.entryAlreadyInCache(group2[k].date, group2[k].title, group2Source[k].source)
            if not inCache:
                db.insertUploadedEvent(group2[k], group2Source[k])
        
        query2 = db.selectAllFromUploadTable().fetchall()
        self.assertEqual(query, query2)
        
        self.assertEqual(False, db.noEntriesWithSourceID(sourceGroup2))
        self.assertEqual(True, db.noEntriesWithSourceID(sourceGroup1))
        
        
        lastEventUploaded = db.getLastEventDateForSourceID(sourceGroup2)
        self.assertEqual("2027-02-04T10:00:00-04:00", lastEventUploaded.isoformat())

        
        
        
if __name__ == "__main__":
    unittest.main()