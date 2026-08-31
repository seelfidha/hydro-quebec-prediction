
import mlflow
from mlflow.tracking import MlflowClient
import h2o
from repository.pannes_repository import get_pannes

if __name__ == '__main__':
    mlflow.set_tracking_uri("http://mlflow:5000")

    # h2o.init()
    # client = MlflowClient()
    # experiment_name = "hydro-quebec-predictions"
    # experiment = client.create_experiment(experiment_name)
    # if experiment is None:
    #     experiement_id = client.create_experiment(experiment_name)
    #     experiment = client.get_experiment(experiement_id)
    # mlflow.set_experiment(experiment_name)

    rows = get_pannes()
    print(rows)

