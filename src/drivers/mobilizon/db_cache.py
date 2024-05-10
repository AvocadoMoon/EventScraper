import sqlite3
from datetime import datetime
import logging
from src.logger import logger_name

logger = logging.getLogger(logger_name)

class UploadedEventRow:
    uuid: str
    id: str
    title: str
    date: str
    groupID: str
    groupName: str
    calendar_id: str
    
    def __init__(self, uuid: str, id: str, title: str, date: str, groupID: str, groupName: str, calendar_id: str):
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
        self.calendar_id = calendar_id
    

class SQLiteDB:
    sql_db_connection: sqlite3.Connection
    uploaded_events_table_name = "uploaded_events"
    
    def __init__(self, inMemorySQLite: bool = False):
        if inMemorySQLite:
            self.sql_db_connection = sqlite3.connect(":memory:")
        else:
            self.sql_db_connection = sqlite3.connect("event_cache.db")
        self.initializeDB()
    
    def initializeDB(self) -> sqlite3.Connection:
        db_cursor = self.sql_db_connection.cursor()
        db_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.uploaded_events_table_name} 
                          (uuid PRIMARY KEY, id, title text, date text, group_id, group_name, calendar_id)""")

    def close(self):
        self.sql_db_connection.close()

    def insertUploadedEvent(self, rowToAdd: UploadedEventRow):
        db_cursor: sqlite3.Cursor = self.sql_db_connection.cursor()
        insertRow = (rowToAdd.uuid, rowToAdd.id, rowToAdd.title, rowToAdd.date, rowToAdd.groupID, rowToAdd.groupName, rowToAdd.calendar_id)
        
        db_cursor.execute(f"INSERT INTO {self.uploaded_events_table_name} VALUES (?, ?, ?, ? , ?, ?, ?)", insertRow)
        self.sql_db_connection.commit()


    # https://www.sqlite.org/lang_datefunc.html
    # Uses built in date time function
    def deleteAllMonthOldEvents(self):
        db_cursor = self.sql_db_connection.cursor()
        db_cursor.execute(f"DELETE FROM {self.uploaded_events_table_name} WHERE datetime(date) < datetime('now', '-1 month')")
        
        self.sql_db_connection.commit()
    
    def selectAllFromTable(self) -> sqlite3.Cursor:
        db_cursor = self.sql_db_connection.cursor()
        res = db_cursor.execute(f"SELECT * FROM {self.uploaded_events_table_name}")
        return res
    
    def selectGroupFromTable(self, groupID):
        db_cursor = self.sql_db_connection.cursor()
        # Comma at the end of (groupID,) turns it into a tuple
        res = db_cursor.execute(f"SELECT * FROM {self.uploaded_events_table_name} WHERE group_id = ?", (groupID,))
        return res
    
    def selectAllRowsWithCalendarID(self, calendar_id):
        db_cursor = self.sql_db_connection.cursor()
        # Comma at the end of (groupID,) turns it into a tuple
        res = db_cursor.execute(f"SELECT * FROM {self.uploaded_events_table_name} WHERE calendar_id = ?", (calendar_id,))
        return res
    
    def getLastEventForCalendarID(self, calendarID) -> datetime:
        db_cursor = self.sql_db_connection.cursor()
        res = db_cursor.execute(f"""SELECT date FROM {self.uploaded_events_table_name} WHERE calendar_id = ?
                                ORDER BY date DESC LIMIT 1""", (calendarID, ))
        # Conversion to ISO format does not like the Z, that represents UTC aka no time zone
        # so using +00:00 is an equivalent to it
        dateString = res.fetchone()[0]
        logger.debug(f"Last date found for calendar ID {calendarID}: {dateString}")
        return datetime.fromisoformat(dateString)
    
    def noEntriesWithCalendarID(self, calendar_id: str) -> bool:
        res = self.selectAllRowsWithCalendarID(calendar_id)
        return len(res.fetchall()) == 0
    
    def entryAlreadyInCache(self, date:str, title:str, calendar_id:str) -> bool:
        db_cursor = self.sql_db_connection.cursor()
        res = db_cursor.execute(f"""SELECT * FROM {self.uploaded_events_table_name} WHERE 
                                date = ? AND title = ? AND calendar_id = ?""", (date, title, calendar_id))
        if(len(res.fetchall()) > 0):
            return True
        return False
        
        
    