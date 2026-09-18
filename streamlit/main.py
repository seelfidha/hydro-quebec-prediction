import requests
import streamlit as st

from utils.data_preprocessor import convert_dict_to_json
from utils.params_config import url_predictor_predict
from utils_streamlit import get_training_status
from utils_streamlit import load_current_call_id, load_panne_by_id, \
    deactivate_data_loading, delete_current_call_id_if_exists, start_training, init_session_vars


def main():
    global values
    st.title("Hydro-quebec data prediction")

    #barside = st.sidebar

    #tab1, tab2, tab3 = st.tabs(["prediction", "Description", "Liste de colonnes"])

    # algorithm :
    # get the current id
    # read information from the api
    # predict next data
    # save to the database if not exist
    #with tab1:
    #init variable current_call_id
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
        st.session_state.show_pannes = True
        panne = st.session_state.current_pannes.pop(0)
        values = vars(panne)
        resp = requests.post(
            url_predictor_predict,
            json= convert_dict_to_json(values),
        )
        print(resp.json())
        st.rerun()

    if st.session_state.get("show_pannes", False) :
        pannes = st.session_state.current_pannes
        if pannes:
            st.dataframe([vars(panne) for panne in pannes])
        else:
            st.info("No pannes to display")

if __name__ == "__main__":
    main()


    #with tab2:
        #pannes = get_pannes()
        #parsed = [row[0] for row in get_columns_names()]
        #st.write(f"Il y'a actuellement {len(pannes)} interruptions enregistrees dans la base de donnees")
        #column_names = []
        #for i in range(len(parsed)):
        #    column_names.append(parsed[i])
        #dataframe = pd.DataFrame(pannes, columns=column_names)
        #st.dataframe(dataframe.head())

        #st.write(dataframe.describe().T)

        #st.write('Liste des colonnes avec le % de données manquantes:')
        #missingSummary = pd.DataFrame({
        #    'Nombre': dataframe.isnull().sum(),
        #    'Pourcentage': (dataframe.isnull().mean() * 100).round(2)
        #})

        #missingSummary = missingSummary[missingSummary['Nombre'] > 0]
        #if missingSummary.empty:
        #    st.success("Aucune donnée manquante.")
        #else:
        #    st.dataframe(missingSummary)

    #with tab3:
        #st.header("Liste de colonnes ")
        #options = [col for col in dataframe.columns if col != "id" and col != "callid_processed"]
        #selected_column = st.selectbox("Colonne", options)
        #st.write(f"La colonne selectionnée est {selected_column}")
        #fig, ax = plt.subplots()
        #ax.hist(dataframe[selected_column].dropna(), bins=20)
        #st.pyplot(fig)