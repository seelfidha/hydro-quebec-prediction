import requests
import streamlit as st

from utils.data_preprocessor import convert_dict_to_json
from utils.params_config import url_predictor_predict, target_column
from utils_streamlit import get_training_status
from utils_streamlit import load_current_call_id, load_panne_by_id, \
    deactivate_data_loading, delete_current_call_id_if_exists, start_training, init_session_vars


def main():
    global values
    st.title("Hydro-quebec data prediction")

    #barside = st.sidebar

    #tab1, tab2, tab3 = st.tabs(["prediction", "Description", "Liste de colonnes"])

    init_session_vars(st)

    #deactivate button stop_collecting_data once current_call_id is not null
    collecting_data_deactivated = st.session_state.get('collecting_data_deactivated')
    stop_collecting_button = st.button(
        "Stop collecting data",
        disabled=collecting_data_deactivated is not None
    )

    get_data_for_prediction_button = st.button(
        "Get data for prediction",
        disabled= collecting_data_deactivated is None or collecting_data_deactivated  is False
    )

    train_model_button = st.button(
        "Train the model",
        disabled= st.session_state.get('current_call_id') is None or st.session_state.get("training_status") == 'RUNNING'
    )

    train_status_button = st.button(
        "Train status",
        disabled= st.session_state.get('training_id') is None
    )

    model_already_trained = st.session_state.get('model_already_trained')
    prediction_button = st.button(
        "Predict first element",
        disabled=model_already_trained is None or model_already_trained is False or st.session_state.get("training_status") == 'RUNNING'
    )

    if stop_collecting_button:
        #deactivate loading data
        deactivate_data_loading()
        st.session_state.collecting_data_deactivated = True
        st.rerun()

    if get_data_for_prediction_button:
        #loadidng current call_id and its interruptions from api
        st.write('Getting next data from server')
        current_call_id = load_current_call_id()
        st.write(f'this call_id: {current_call_id} will be deleted from database if exists')
        st.session_state.current_call_id = current_call_id

        #loading interruptions
        pannes = load_panne_by_id(current_call_id)
        print(f"number of interruptions found  {len(pannes)}")

        st.session_state.current_pannes = pannes
        st.session_state.show_pannes = True
        #delete current call id if already saved to database
        print(f"delete current call_id if exists {current_call_id}")
        delete_current_call_id_if_exists(current_call_id, st)
        st.rerun()

    if train_model_button:
        print(f"Starting training")
        run_id = start_training()
        print(f"training started with id {run_id}")
        st.session_state.training_id = run_id
        st.session_state.training_status = "RUNNING"
        st.rerun()

    if train_status_button:
        training_id = st.session_state.get('training_id')
        status = get_training_status(training_id)
        print("training status: ",status)
        st.write("the training process is in status: ",status)
        st.session_state.training_status = status
        if status == 'FINISHED':
            st.session_state.model_already_trained = True
        st.rerun()

    if prediction_button:

        json = get_first_element_as_json()
        if json[target_column] is None or json['cause'] =='':
            print("------------------------------------------------")
            print("Missing data for end date or cause, cannot run prediction")
            st.rerun()

        target = json.pop(target_column)
        st.session_state.prediction_target_value = target
        try:
            resp = requests.post(
                url_predictor_predict,
                json=json,
            )
            st.session_state.display_prediction = True
        except Exception :
            print(f'Error in prediction')
            resp = None
            st.session_state.display_prediction = False

        if resp is not None:
            st.session_state.prediction_estimated_value = resp.json().get("prediction")
        else:
            print(f'Cannot predict target value, real value is {target}')
        st.rerun()

    if st.session_state.get("show_pannes", False) :
        pannes = st.session_state.current_pannes
        if pannes:
            st.dataframe([vars(panne) for panne in pannes])
        else:
            st.info("No pannes to display")


    if st.session_state.get("display_prediction") :
        st.write(f'real target value: {st.session_state.get('prediction_target_value')} ')
        st.write(f'predicted value: {st.session_state.get("prediction_estimated_value")['predict']['0']}')
        print(f'real target value vs predicted value: '
              f'{st.session_state.get('prediction_target_value')} : '
              f'{st.session_state.get("prediction_estimated_value")['predict']['0']}')
    else:
        st.write(f'real target value: {st.session_state.get('prediction_target_value')}')

def get_first_element_as_json():
    st.session_state.show_pannes = True
    panne = st.session_state.current_pannes.pop(0)
    values = vars(panne)
    json_format_values = convert_dict_to_json(values)
    return json_format_values

if __name__ == "__main__":
    main()
