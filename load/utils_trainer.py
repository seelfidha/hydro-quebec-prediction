import json
from _pydatetime import timedelta
from datetime import datetime

import requests

from repository.pannes_repository import save_new_panne
from repository.processed_id_repository import is_not_processed, save_as_processed
from utils.params_config import LOADER_MINUTES_OFFSET


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

def empty_to_none(value):
    if value == "":
        return None
    return value

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

def execute_data_collection():
    now = datetime.now()
    print(f'Current execution at {now}', flush=True)
    url_ID = 'https://pannes.hydroquebec.com/pannes/donnees/v3_0/bisversion.json'
    respID = requests.get(url_ID)
    respID.raise_for_status()
    callID = respID.json()
    print(f'this call_id: {callID} will be processed if it is not already saved in bd')
    if is_not_processed(callID):
        print(f'new call_id {callID} detected ')
        result = save_as_processed(callID)
        if result:
            print(f'new call_id {callID}  saved to db')
            url_data = f'https://pannes.hydroquebec.com/pannes/donnees/v3_0/bismarkers{callID}.json'
            respData = requests.get(url_data)
            respData.raise_for_status()
            # parse interruption data
            data = respData.json()
            for panne_json in data['pannes']:
                newPanne = create_new_interruption_from_json(callID, panne_json)
                save_new_panne(callID, newPanne)
        else:
            print(f'error saving call_id {callID}')
    else:
        print(f"this call_id {callID} is already processed")
    print(f'Next execution at %s', (now + timedelta(minutes=LOADER_MINUTES_OFFSET)))