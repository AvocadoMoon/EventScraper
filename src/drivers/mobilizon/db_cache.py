import sqlite3
from datetime import datetime


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

class SQLiteDB:
    sql_db_connection: sqlite3.Connection
    uploaded_events_table_name = "uploaded_events"
    
    def connectAndInitializeDB(self) -> sqlite3.Connection:
        sql_db_connection = sqlite3.connect("event_cache.db")
        db_cursor = sql_db_connection.cursor()

        db_cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.uploaded_events_table_name} 
                          (uuid PRIMARY KEY, id, title text, date text, group_id, group_name)""")
        self.sql_db_connection = sql_db_connection

    def close(self):
        self.sql_db_connection.close()

    def insertUploadedEvent(self, rowsToAdd: [UploadedEventRow]):
        db_cursor: sqlite3.Cursor = self.sql_db_connection.cursor()
        insertArray = []
        for row in rowsToAdd:
            insertArray.append((row.uuid, row.id, row.title, row.date, row.groupID))
        
        db_cursor.executemany(f"INSERT INTO {self.uploaded_events_table_name} VALUES (?, ?, ?, ? , ?, ?)", insertArray)
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
    
    # TODO: Create SQL that does this
    def getLastEventForCalendarID(self, calendarID) -> datetime:
        pass
        
        
    