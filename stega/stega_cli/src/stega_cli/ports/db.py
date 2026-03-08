import contextlib
import sqlite3
import typing as T


_TABLES = (


)


@contextlib.contextmanager
def acquire_connection(db_path: str) -> T.Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


def init_db(db_path: str) -> None:
    with acquire_connection(db_path) as conn:
        cursor = conn.cursor()
        for table in _TABLES:
            cursor.execute(table)
        connt.commit()

