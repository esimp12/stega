import sqlite3
import typing as T


def get_entity_id(
    conn: sqlite3.Connection,
    correlation_id: str,
) -> T.Optional[str]:
    """Get the entity id correlated with a client action."""
    with conn.cursor() as cur:
        res = cur.execute("""
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


def create_correlation(
    conn: sqlite3.Connection,
    correlation_id: str,
    entity_id: str,
) -> None:
    pass
    # TODO: insert correlation_id, entity_id into table
