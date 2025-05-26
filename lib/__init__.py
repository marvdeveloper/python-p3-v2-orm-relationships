import sqlite3

CONN = sqlite3.connect('company.db', timeout=30, check_same_thread=False)
CONN.execute("PRAGMA foreign_keys = ON;")
CURSOR = CONN.cursor()
