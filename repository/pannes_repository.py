import psycopg

from repository.repository_config import get_connection, get_connection_with_retries


def get_pannes():
    conn = get_connection_with_retries(10, 3)
    try :
        with conn.cursor() as cursor:
            query = "SELECT * FROM pannes ORDER BY id DESC"
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
    except psycopg.OperationalError as error:
        print(f"Error getting data from table pannes {error}")

def save_new_panne(item_id, data):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = """
                    INSERT INTO pannes \
                    (nb_clients_impactes, date_debut, date_fin, pannep, \
                     longitude, latitude,\
                     statut, info_non_utilise, cause, id_municipalite, id_msg_panne, callID_processed) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                    ON CONFLICT (id) DO NOTHING; \
                    """

            params = (data.nb_clients_impactes,
                      data.date_debut,
                      data.date_fin,
                      data.pannep,
                      data.longitude,
                      data.latitude,
                      data.statut,
                      data.info_non_utilise,
                      data.cause,
                      data.id_municipalite,
                      data.id_msg_panne,
                      data.callID_processed
                      )

            cursor.execute(query, params)
            conn.commit()
    except Exception as e :
        print(f"error saving interruption data for id: %s with error: %s", item_id, e)
        conn.rollback()