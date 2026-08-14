import sqlite3


def get_entity_id(conn: sqlite3.Connection, correlation_id: str) -> str | None:
    cur = conn.cursor()
    row = cur.execute(
        """
        SELECT
          entity_id
        FROM
          actions
        WHERE
          correlation_id = :correlation_id
        """,
        {"correlation_id": correlation_id},
    ).fetchone()
    return None if row is None else row[0]


def insert_correlation(conn: sqlite3.Connection, correlation_id: str, entity_id: str) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO actions (correlation_id, entity_id) VALUES(:correlation_id, :entity_id)
        """,
        {
            "correlation_id": correlation_id,
            "entity_id": entity_id,
        },
    )
