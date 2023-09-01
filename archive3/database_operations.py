import sqlite3

def connect_to_database(db_name='wow_cards.db'):
    """Establish connection to the SQLite database."""
    return sqlite3.connect(db_name)

def query_database(cursor, query, params=()):
    """Execute a query and fetch all results."""
    cursor.execute(query, params)
    return cursor.fetchall()

def insert_into_database(cursor, query, params=()):
    """Execute an insert operation."""
    cursor.execute(query, params)
