import sqlite3
import os

# create a path to the database file so that it can run, not dependent on the location of the project
DataBasePath = os.path.join(os.path.dirname(__file__),"expenses.db") 

def OpenDBConn() -> sqlite3.Connection:
    conn = sqlite3.connect(DataBasePath)
    # ensure the DB acts like a dictionary, rather than location array items (e.g arr[0])
    conn.row_factory = sqlite3.Row
    return conn 

def DataBaseSetup() -> None:
    with OpenDBConn() as conn:
        # table creation, further restriction of inputs to limit invalid responses
        conn.execute("""
CREATE TABLE IF NOT EXISTS expenses (   
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    cost_gbp REAL NOT NULL CHECK (cost_gbp >= 0),
    description TEXT NOT NULL,
    expense_type TEXT NOT NULL CHECK (expense_type IN ('travel', 'food', 'other'))
);
            """)
        conn.commit()