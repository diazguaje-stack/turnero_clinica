import sqlite3

def get_db():
    conn = sqlite3.connect("turnero.db",timeout=30)
    conn.row_factory = sqlite3.Row



    return conn
