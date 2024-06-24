from src.db_cache import SQLiteDB, UploadedEventRow, UploadSource, SourceTypes
import sqlite3
import os
import unittest

# TODO: Test getting the last event uploaded for a specific group

class TestEventTable(unittest.TestCase):
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
    
    def insertGroup(self, db: SQLiteDB, group: [], groupSource: []):
        for k in range(len(group)):
            db.insertUploadedEvent(group[k], groupSource[k])
    
    def test_GroupInsertionAndRetrieval(self):
        db = SQLiteDB(True)
        self.insertGroup(db, self.group1, self.group1Source)
             
        query = db.selectAllFromUploadTable().fetchall()
        self.assertEqual(len(query), len(self.group1), "Ensure group 1 has been fully inserted")
        
        query = db.selectAllRowsWithCalendarID(self.sourceGroup1).fetchall()
        self.assertEqual(len(query), len(self.group1), "Getting groups work when alone")
        
        self.insertGroup(db, self.group2, self.group2Source)
        query = db.selectAllFromUploadTable().fetchall()
        self.assertEqual(len(query), (len(self.group1) + len(self.group2)), "Inserting another unique group ensures all are in")
        
        query = db.selectAllRowsWithCalendarID(self.sourceGroup2).fetchall()
        self.assertEqual(len(query), len(self.group2), "Ensure only selected group is taken when there's multiple groups")
        for row in query:
            self.assertEqual(row[7], self.sourceGroup2)
    
    
    def test_RemoveOldEvents(self):
        db = SQLiteDB(True)
        
        self.insertGroup(db, self.group1, self.group1Source)
        self.insertGroup(db, self.group2, self.group2Source)
        
        db.deleteAllMonthOldEvents()
        query = db.selectAllFromUploadTable().fetchall()
        self.assertEqual(len(query), len(self.group2), "Ensure that all old events are deleted and only new ones are left")
        for row in query:
            self.assertEqual(row[5], self.group2Name)
        
    def test_UniqueInsertion(self):
        db = SQLiteDB(True)
        
        self.insertGroup(db, self.group1, self.group1Source)
        self.insertGroup(db, self.group2, self.group2Source)
        # Ensure only Unique UUIDs are inserted
        self.assertRaises(sqlite3.IntegrityError, db.insertUploadedEvent, self.group2[0], self.group2Source[0])
        
    
    def test_IdempotentInsertionsAndCaching(self):
        db = SQLiteDB(True)
        
        self.insertGroup(db, self.group2, self.group2Source)
        query = db.selectAllFromUploadTable().fetchall()
        
        for k in range(len(self.group2)):
            inCache = db.entryAlreadyInCache(self.group2[k].date, self.group2[k].title, self.group2Source[k].source)
            if not inCache:
                db.insertUploadedEvent(self.group2[k], self.group2Source[k])
        
        query2 = db.selectAllFromUploadTable().fetchall()
        self.assertEqual(query, query2)
        
        self.assertEqual(False, db.noEntriesWithSourceID(self.sourceGroup2))
        self.assertEqual(True, db.noEntriesWithSourceID(self.sourceGroup1))
        
    
    def test_GetLastEvent(self):
        db = SQLiteDB(True)
        
        self.insertGroup(db, self.group2, self.group2Source)
        lastEventUploaded = db.getLastEventDateForSourceID(self.sourceGroup2)
        self.assertEqual("2027-02-04T10:00:00-04:00", lastEventUploaded.isoformat())

        
        
        
if __name__ == "__main__":
    unittest.main()