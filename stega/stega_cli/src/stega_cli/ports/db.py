import contextlib
import sqlite3
import typing as T


@contextlib.contextmanager
def acquire_connection(db_name: str) -> T.Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_name)
    yield conn
    conn.close()

