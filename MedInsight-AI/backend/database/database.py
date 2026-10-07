import sqlite3
from contextlib import contextmanager

from backend import config
from backend.database.models import SCHEMA


@contextmanager
def connect():
    conn = sqlite3.connect(config.DB_PATH)
    try:
        conn.execute(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()
