import json
from datetime import datetime, timedelta

import psycopg
import requests
from apscheduler.schedulers.blocking import BlockingScheduler

MINUTES_OFFSET = 3

def get_connection():
    return psycopg.connect(
        host='postgres',
        dbname='test_db',
        user='root',
        password='root',
        port=5432
    )

def is_not_processed(conn, item_id):
    with conn.cursor() as cursor:
        cursor.execute('SELECT 1 FROM processed_ids where id =%s', (item_id,))
        return cursor.fetchone() is None

def mark_as_processed(conn, item_id):
    try:
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

def create_new_interruption_from_json(callID, panne):
    newPanne = Panne()
    newPanne.callID_processed = callID
    newPanne.nb_clients_impactes = panne[0]
    newPanne.date_debut = panne[1]
    newPanne.date_fin = empty_to_none(panne[2])
    newPanne.pannep = panne[3]
    longitude, latitude = json.loads(panne[4])
    newPanne.longitude = longitude
    newPanne.latitude = latitude
    newPanne.statut = panne[5]
    newPanne.info_non_utilise = panne[6]
    newPanne.cause = panne[7]
    newPanne.id_municipalite = panne[8]
    newPanne.id_msg_panne = panne[9]
    return newPanne

def empty_to_none(value):
    if value == "":
        return None
    return value

def save_interruption(conn, item_id, data):
    try:
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

class Panne():
    callID_processed: int
    id: int #= Field(..., description="identifiant interne de l'interruption")
    nb_clients_impactes: int #= Field(..., description= "nombre de clients impactes")
    date_debut: str #= Field(..., description="")
    date_fin: str #= Field(..., description="")
    pannep: str #= Field(..., description="")
    longitude: str #= Field(..., description= "")
    latitude: str #= Field(..., description= "")
    statut: str #= Field(..., description= "")
    info_non_utilise: str #= Field(..., description="")
    cause: str #= Field(..., description="")
    id_municipalite: int #= Field(..., description="")
    id_msg_panne: int #= Field(..., description="")

scheduler = BlockingScheduler()
#periodically get the data
@scheduler.scheduled_job("interval", minutes= MINUTES_OFFSET)
def collect_data() :
    now = datetime.now()
    print(f'Current execution at %s', now)
    url_ID = 'https://pannes.hydroquebec.com/pannes/donnees/v3_0/bisversion.json'
    respID = requests.get(url_ID)
    respID.raise_for_status()
    callID = respID.json()
    print(f'this call_id: {callID} will be processed if it is not already saved in bd')
    conn = get_connection()
    if is_not_processed(conn, callID):
        print(f'new call_id {callID} detected ')
        result = mark_as_processed(conn, callID)
        if result:
            print(f'new call_id {callID}  saved to db')
            url_data = f'https://pannes.hydroquebec.com/pannes/donnees/v3_0/bismarkers{callID}.json'
            respData = requests.get(url_data, callID)
            # parse interruption data
            data = respData.json()
            for panne_json in data['pannes']:
                newPanne = create_new_interruption_from_json(callID, panne_json)
                save_interruption(conn, callID, newPanne)
        else:
            print(f'error saving call_id {callID}')
    else:
        print(f"this call_id {callID} is already processed")
    print(f'Next execution at %s', (now + timedelta(minutes=MINUTES_OFFSET)))

###########START RUNNING############
####################################
scheduler.start()
####################################
####################################
