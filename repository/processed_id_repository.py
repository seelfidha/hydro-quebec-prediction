from repository.repository_config import get_connection


def is_not_processed(item_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1 FROM processed_ids where id =%s', (item_id,))
            return cursor.fetchone() is None
    except Exception as e :
        print(f"error checking id already processed: {item_id}")
        conn.rollback()
        return False

def mark_as_processed(item_id):
    try:
        conn = get_connection()
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
    except Exception as e :
        print(f"error saving id: %s", item_id)
        conn.rollback()
        return False