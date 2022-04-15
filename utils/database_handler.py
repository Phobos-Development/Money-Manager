import sqlite3

from sqlite3 import Error


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('income_manager.db')
    except Error as e:
        print(f"[SQLite] Error Occurred {e}")
    return conn


def execute_sql(conn, sql_data, args=None):
    try:
        c = conn.cursor()
        if args is None:
            c.execute(sql_data)
        else:
            c.execute(sql_data, args)
        conn.commit()
        conn.close()
    except Error as e:
        print(f"[SQLite] Error Occurred {e}")


def query_sql(conn, sql_data, args=None, one=True):
    c = None
    try:
        c = conn.cursor()
        if args is None:
            c.execute(sql_data)
        else:
            c.execute(sql_data, args)
    except Error as e:
        print(e)
    finally:
        if one:
            data = c.fetchone()
        else:
            data = c.fetchall()
        conn.close()
        return data


def setup():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS income(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id INT,
            year INT,
            month INT,
            day INT,
            amount INT,
            note TEXT DEFAULT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS income_channels(
            discord_id INT PRIMARY KEY,
            channel_id INT DEFAULT NULL
        )
        """
    )
    for cmd in commands:
        execute_sql(create_connection(), cmd)
    print("DB Ready")