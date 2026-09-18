
db_host = "dpg-daec7eht0dsc739l7i50-a"#postgres#localhost
db_port = "5432"
db_name = "interruption_db"
db_user = "root"
db_pw = "4WvlYwM7SbMfxp27cToQHC62tw1giS8a"#root

ml_flow_host = "http://mlflow"
ml_flow_port = "5000"
ml_flow_url = ml_flow_host+":"+ml_flow_port

h2o_host = "127.0.0.1"
h2o_port = "5000"

minio_host = "minio"
minio_port = "9000"
minio_url = minio_host+":"+minio_port
minio_access_key = "admin"
minio_secret = "strongpassword"

LOADER_MINUTES_OFFSET = 3
loader_fast_api_host = "0.0.0.0"
loader_fast_api_port = 8501
url_loader_deactivate = "http://localhost:8501/collect_data/deactivate"
url_loader_delete_if_exists = "http://localhost:8501/collect_data/delete/{current_call_id}"

trainer_fast_api_host = "0.0.0.0"
trainer_fast_api_port = 8502
url_trainer_start_training = "http://localhost:8502/train_data/start"
url_trainer_status_training = "http://localhost:8502/train_data/status/{training_id}"

predictor_fast_api_host = "0.0.0.0"
predictor_fast_api_port = 8503
url_predictor_predict = "http://localhost:8503/predict"


hydro_quebec_url_ID = 'https://pannes.hydroquebec.com/pannes/donnees/v3_0/bisversion.json'
hydro_quebec_url_data = 'https://pannes.hydroquebec.com/pannes/donnees/v3_0/bismarkers{callID}.json'
