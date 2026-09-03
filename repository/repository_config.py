import time

import psycopg

from utils.params_config import db_host, db_name, db_user, db_pw, db_port


def get_connection_with_retries(max_retries=10, delay_seconds=3):
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return get_connection()
        except psycopg.OperationalError as error:
            last_error = error
            print(f"Database connection failed on attempt {attempt} error: {last_error}", flush=True)
            if attempt < max_retries:
                time.sleep(delay_seconds)
    raise last_error

def get_connection():
    return psycopg.connect(
        host=db_host,
        dbname=db_name,
        user=db_user,
        password=db_pw,
        port=db_port
    )
