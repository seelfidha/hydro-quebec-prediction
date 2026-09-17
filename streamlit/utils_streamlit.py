import json

import requests

from load.utils_loader import Panne
from utils.params_config import hydro_quebec_url_data, hydro_quebec_url_ID, url_loader_deactivate, \
    url_loader_delete_if_exists, url_trainer_start_training, url_trainer_status_training


def init_session_vars(st):
    if "current_call_id" not in st.session_state:
        st.session_state.current_call_id = None

    if "current_pannes" not in st.session_state:
        st.session_state.current_pannes = None

    if "training_id" not in st.session_state:
        st.session_state.training_id = None

    if "training_status" not in st.session_state:
        st.session_state.training_status = None

    if "model_already_trained" not in st.session_state:
        st.session_state.model_already_trained = False

def get_training_status(training_id):
    url = url_trainer_status_training.replace('{training_id}', training_id)
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()["run_id"]

def start_training():
    resp = requests.post(url_trainer_start_training)
    resp.raise_for_status()
    return resp.json()["run_id"]

def deactivate_data_loading():
    resp = requests.post(url_loader_deactivate)
    resp.raise_for_status()

def load_current_call_id():
    respID = requests.get(hydro_quebec_url_ID)
    respID.raise_for_status()
    callID = respID.json()
    return callID

def load_panne_by_id(callID):
    url_data = hydro_quebec_url_data.replace('{callID}', callID)
    print(f'url_data: {url_data}')
    respData = requests.get(url_data)
    respData.raise_for_status()
    # parse interruption data
    data = respData.json()
    pannes = []
    for panne_json in data['pannes']:
        newPanne = create_new_interruption_from_json(callID, panne_json)
        pannes.append(newPanne)
    return pannes


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

def delete_current_call_id_if_exists(current_call_id, st):
    resp = requests.delete(url_loader_delete_if_exists.replace('{current_call_id}', current_call_id))
    if resp.status_code == 200:
        st.write(f'call_id: {current_call_id} deleted from database if exists')
    else:
        st.write(f'error deleting call_id: {current_call_id} from database')