from repository.repository_config import get_connection_with_retries


def is_not_processed(item_id):
    try:
        with get_connection_with_retries(10, 3) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT 1 FROM processed_ids where id =%s', (item_id,))
                return cursor.fetchone() is None
    except Exception:
        print(f"error checking id already processed: {item_id}")
        raise

def mark_as_processed(item_id):
    try:
        with get_connection_with_retries(10, 3) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO processed_ids (id)
                    VALUES (%s) ON CONFLICT (id) DO NOTHING
                    """,
                    (item_id,)
                )
                conn.commit()
                return True
    except Exception:
        print(f"error saving id: {item_id}")
        raise
