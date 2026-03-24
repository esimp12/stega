import sqlite3


def get_entity_id(
    conn: sqlite3.Connection,
    correlation_id: str,
) -> str | None:
    """Get the entity id correlated with a client action."""
    with conn.cursor() as cur:
        res = cur.execute(
            """
        SELECT
          entity_id,
        FROM
          actions
        WHERE
          correlation_id = :correlation_id 
        """,
            {"correlation_id": correlation_id},
        )
        entity_id = res.fetchone()

    # no entity found for correlation id
    if entity_id is None:
        return None

    return entity_id


def insert_correlation(
    conn: sqlite3.Connection,
    correlation_id: str,
    entity_id: str,
) -> None:
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
