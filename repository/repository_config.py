import time

import psycopg

def get_connection_with_retries(max_retries=10, delay_seconds=3):
    last_error = None
    for attempt in range(1, max_retries +1):
        try:
            return get_connection()
        except psycopg.OperationalError as error :
            last_error = error
            print(f"Database connection failed on attempt {attempt} error: {last_error}", flush=True)
            if attempt < max_retries:
                time.sleep(delay_seconds)

def get_connection():
    return psycopg.connect(
        host='postgres',
        dbname='test_db',
        user='root',
        password='root',
        port=5432
    )