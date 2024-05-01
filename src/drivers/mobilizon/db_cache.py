import sqlite3


class UploadedEventRow:
    uuid: str
    id: str
    title: str
    date: str
    groupID: str
    
    def __init__(self, uuid: str, id: str, title: str, date: str, groupID: str):
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


def connectAndInitializeDB() -> sqlite3.Connection:
    sql_db_connection = sqlite3.connect("event_cache.db")
    db_cursor = sql_db_connection.cursor()

    db_cursor.execute("CREATE TABLE uploaded_events(uuid, id, title text, date text, group_id)")
    return sql_db_connection


def insertUploadedEvent(sql_db_connection: sqlite3.Connection, rowsToAdd: [UploadedEventRow]):
    db_cursor: sqlite3.Cursor = sql_db_connection.cursor()
    insertArray = []
    for row in rowsToAdd:
        insertArray.append((row.uuid, row.id, row.title, row.date, row.groupID))
    
    db_cursor.executemany("INSERT INTO uploaded_events VALUES (?, ?, ?, ? , ?)", insertArray)
    sql_db_connection.commit()


# https://www.sqlite.org/lang_datefunc.html
# Uses built in date time function
def deleteAllMonthOldEvents(sql_db_connection: sqlite3.Connection):
    db_cursor = sql_db_connection.cursor()
    db_cursor.execute("DELETE FROM uploaded_events WHERE datetime(date) < datetime('now', '-1 month')")
    
    sql_db_connection.commit()
    