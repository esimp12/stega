import contextlib
from dataclasses import dataclass

import psycopg2
import typing_extensions as T
from psycopg2.extensions import connection


@dataclass
class DbConnArgs:
    """Database connection arguments.

    Attributes:
        dbname (str): Database name.
        username (str): Username for the database.
        password (str): Password for the database.
        host (str): Host where the database is located.
        port (int): Port number for the database connection.
    """

    dbname: str
    username: str
    password: str
    host: str
    port: int


@contextlib.contextmanager
def acquire_connection(dbargs: DbConnArgs) -> T.Generator[connection, None, None]:
    """Acquire a connection to the database.

    Args:
        dbargs (DbConnArgs): Database connection arguments.

    Yields:
        conn: A connection to the database.
    """
    conn = psycopg2.connect(
        dbname=dbargs.dbname,
        user=dbargs.username,
        password=dbargs.password,
        host=dbargs.host,
        port=dbargs.port,
        async_=True,
    )
    with conn:
        yield conn
        conn.close()
