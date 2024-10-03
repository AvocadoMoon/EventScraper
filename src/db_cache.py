import sqlite3
from datetime import datetime
import logging
from src.logger import logger_name
import os

logger = logging.getLogger(logger_name)

class UploadedEventRow:
    uuid: str
    id: str
    title: str
    date: str
    groupID: str
    groupName: str
    
    def __init__(self, uuid: str, id: str, title: str, date: str, groupID: str, groupName: str):
        """_summary_

        Args:
            uuid (str): _description_
            id (str): _description_
            title (str): _description_
            date (str): Has to be of format ISO8601 that is YYYY-MM-DD HH:MM:SS.SSS. Can also have T in the center if desired.
            groupID (str): _description_
        """
        
        self.uuid = uuid
        self.id = id
        self.title = title
        self.date = date
        self.groupID = groupID
        self.groupName = groupName

class UploadSource:
    uuid: str
    websiteURL: str
    source: str
    sourceType: str
    
    def __init__(self, uuid:str, websiteURL: str, source:str, sourceType: str):
        self.uuid = uuid
        self.websiteURL = websiteURL
        self.source = source
        self.sourceType = sourceType

class ScraperTypes:
    json = "JSON"
    gCal = "Google Calendar" 

class SQLiteDB:
    sql_db_connection: sqlite3.Connection
    uploaded_events_table_name = "uploaded_events"
    event_source_table_name = "event_source"
    
    allColumns = f"""{uploaded_events_table_name}.uuid, {uploaded_events_table_name}.id,
    {uploaded_events_table_name}.title, {uploaded_events_table_name}.date, 
    {uploaded_events_table_name}.group_id, {uploaded_events_table_name}.group_name,
    {event_source_table_name}.websiteURL, {event_source_table_name}.source, {event_source_table_name}.sourceType"""
    
    def __init__(self, inMemorySQLite: bool = False):
        if inMemorySQLite:
            self.sql_db_connection = sqlite3.connect(":memory:")
        else:
            cache_db_path = os.environ.get("CACHE_DB_PATH")
            if cache_db_path is not None:
                self.sql_db_connection = sqlite3.connect(cache_db_path + "/event_cache.db")
            else:
                self.sql_db_connection = sqlite3.connect("event_cache.db")
        self.initializeDB()
    
    def initializeDB(self) -> sqlite3.Connection:
        db_cursor = self.sql_db_connection.cursor()
        db_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.uploaded_events_table_name} 
                          (uuid PRIMARY KEY, id, title text, date text, group_id, group_name)""")
        db_cursor.execute(f"""CREATE  TABLE IF NOT EXISTS {self.event_source_table_name}
                          (uuid, websiteURL text, source text, sourceType text, 
                          FOREIGN KEY (uuid) REFERENCES uploaded_events(uuid) ON DELETE CASCADE)""" )

    def close(self):
        self.sql_db_connection.close()

    # https://www.sqlite.org/lang_datefunc.html
    # Uses built in date time function
    def deleteAllMonthOldEvents(self):
        db_cursor = self.sql_db_connection.cursor()
        db_cursor.execute(f"DELETE FROM {self.uploaded_events_table_name} WHERE datetime(date) < datetime('now', '-1 month')")
        
        self.sql_db_connection.commit()

    def selectAllRowsWithCalendarID(self, source):
        db_cursor = self.sql_db_connection.cursor()
        # Comma at the end of (groupID,) turns it into a tuple
        res = db_cursor.execute(f"""SELECT {self.allColumns} FROM {self.uploaded_events_table_name} 
                                INNER JOIN {self.event_source_table_name} ON 
                                {self.uploaded_events_table_name}.uuid={self.event_source_table_name}.uuid
                                WHERE source = ?""", (source,))
        return res
    
    def getLastEventDateForSourceID(self, calendarID) -> datetime:
        db_cursor = self.sql_db_connection.cursor()
        res = db_cursor.execute(f"""SELECT date FROM {self.uploaded_events_table_name}
                                INNER JOIN {self.event_source_table_name} ON 
                                {self.uploaded_events_table_name}.uuid={self.event_source_table_name}.uuid
                                WHERE source = ?
                                ORDER BY date DESC LIMIT 1""", (calendarID, ))
        # Conversion to ISO format does not like the Z, that represents UTC aka no time zone
        # so using +00:00 is an equivalent to it
        dateString = res.fetchone()[0]
        logger.debug(f"Last date found for calendar ID {calendarID}: {dateString}")
        return datetime.fromisoformat(dateString)
    
    def noEntriesWithSourceID(self, calendar_id: str) -> bool:
        res = self.selectAllRowsWithCalendarID(calendar_id)
        return len(res.fetchall()) == 0
    
    def entryAlreadyInCache(self, date:str, title:str, sourceID:str) -> bool:
        db_cursor = self.sql_db_connection.cursor()
        res = db_cursor.execute(f"""SELECT {self.allColumns} FROM {self.uploaded_events_table_name}
                                INNER JOIN {self.event_source_table_name} ON 
                                {self.uploaded_events_table_name}.uuid={self.event_source_table_name}.uuid
                                WHERE date = ? AND title = ? AND source = ?""", (date, title, sourceID))
        query = res.fetchall()
        if(len(query) > 0):
            return True
        return False

    def insertUploadedEvent(self, rowToAdd: UploadedEventRow, eventSource: UploadSource):
        db_cursor: sqlite3.Cursor = self.sql_db_connection.cursor()
        insertRow = (rowToAdd.uuid, rowToAdd.id, rowToAdd.title, rowToAdd.date, rowToAdd.groupID, rowToAdd.groupName)
        eventSourceRow= (eventSource.uuid, eventSource.websiteURL, eventSource.source, eventSource.sourceType)
        
        db_cursor.execute(f"INSERT INTO {self.uploaded_events_table_name} VALUES (?, ?, ?, ? , ?, ?)", insertRow)
        db_cursor.execute(f"INSERT INTO {self.event_source_table_name} VALUES (?, ? , ?, ?)", eventSourceRow)
        self.sql_db_connection.commit()
    
    def selectAllFromUploadTable(self) -> sqlite3.Cursor:
        db_cursor = self.sql_db_connection.cursor()
        res = db_cursor.execute(f"SELECT * FROM {self.uploaded_events_table_name}")
        return res
    
    
        
        
    