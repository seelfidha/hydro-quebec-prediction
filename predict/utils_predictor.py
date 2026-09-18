import mlflow
import mlflow.pyfunc
from mlflow import MlflowClient

from utils.params_config import ml_flow_url

mlflow_client = MlflowClient(tracking_uri=ml_flow_url)

def get_model_champion():
    return mlflow.pyfunc.load_model("models:/hydro-quebec-customers@champion")

# def get_model_champion_info():
#     return mlflow_client.get_model_version_by_alias("my_model","champion")

# def get_prediction(payload):
#
#     pandas_frame = pd.DataFrame([payload])
#     pandas_frame = handle_h2o_categorical_data(pandas_frame)
#     new_frame = h2o.H2OFrame(pandas_frame)
#     return get_model_champion().predict(new_frame)
