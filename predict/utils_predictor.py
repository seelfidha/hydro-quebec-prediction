import mlflow
import mlflow.pyfunc
from mlflow import MlflowClient

from utils.params_config import ml_flow_url

mlflow_client = MlflowClient(tracking_uri=ml_flow_url)

def get_model_champion():
    return mlflow.pyfunc.load_model("model:/hydro-quebec-customers@champion")